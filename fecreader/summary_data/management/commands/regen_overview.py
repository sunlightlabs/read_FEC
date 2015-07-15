## godawful mess to redo some static pages. 

## Need to factor out all the cycle_list stuff; why is everything always done on deadline anyways? 

from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Sum, Count
from django.core.management.base import BaseCommand, CommandError

from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site

from django.conf import settings

from formdata.models import SkedE
from summary_data.models import Committee_Overlay
from fec_alerts.models import WebK
from ftpdata.models import Committee
from shared_utils.cycle_utils import cycle_calendar, cycle_fake



# this will fail if there are two sites! Getting a site by name is annoying for local dev. There's a better solution than this, but... 

this_site = Site.objects.all()[0]


try:
    ACTIVE_CYCLES = settings.ACTIVE_CYCLES
except:
    print "Missing active cycle list. Defaulting to 2016. "
    ACTIVE_CYCLES = ['2016']


PROJECT_ROOT = settings.PROJECT_ROOT


class Command(BaseCommand):
    help = "Regenerates most of the overview pages: main, outside_money, superpac, dark_money and connected."
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
        for cycle in ACTIVE_CYCLES:
            
            cycle_details = cycle_calendar[int(cycle)]
            CYCLE_START = cycle_details['start']
            CYCLE_END = cycle_details['end']
        
            update_time = datetime.now()
        
            print "Running outside spending summaries"
            summary_obj = {}
        
            all_independent_expenditures = SkedE.objects.filter(superceded_by_amendment=False, effective_date__gte=CYCLE_START, effective_date__lte=CYCLE_END)
            summary_obj['ie_sum'] = all_independent_expenditures.aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
            print "\tpositive vs negative"
            # postive vs negative
            summary_obj['positive'] = all_independent_expenditures.filter(support_oppose_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
            summary_obj['negative'] = all_independent_expenditures.filter(support_oppose_checked='O').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']

            print "\ttarget party breakdown"
            # breakdown by target party
            summary_obj['pro_dem'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
            summary_obj['pro_rep'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
            summary_obj['anti_dem'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
            summary_obj['anti_rep'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
            print "\toffice breakdown"
            # breakdown by target party
            summary_obj['senate'] = all_independent_expenditures.filter(candidate_office_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
            summary_obj['house'] = all_independent_expenditures.filter(candidate_office_checked='H').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
       
        
            all_outside_spenders = Committee_Overlay.nulls_last_objects.filter(total_indy_expenditures__gt=0, cycle=str(cycle))
            print "\toutside spending types"
            # breakdown by types:
            summary_obj['party_committees'] = all_outside_spenders.filter(ctype__in=('X', 'Y', 'Z')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            # includes hybrids
            summary_obj['super_pacs'] = all_outside_spenders.filter(ctype__in=('O', 'U', 'V', 'W')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            # non-committees:
            summary_obj['non_committees'] = all_outside_spenders.filter(ctype__in=('I')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            summary_obj['oth_committees'] = all_outside_spenders.filter(ctype__in=('N', 'Q')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            summary_obj['house_committees'] = all_outside_spenders.filter(ctype__in=('H')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            summary_obj['senate_committees'] = all_outside_spenders.filter(ctype__in=('S')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        
        
            print "\toutside spending parties"
            # breakdown by parties 
            summary_obj['dem_affil'] = all_outside_spenders.filter(political_orientation='D').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            summary_obj['rep_affil'] = all_outside_spenders.filter(political_orientation='R').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
            summary_obj['no_affil'] = all_outside_spenders.exclude(political_orientation__in=('R', 'D')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        
        
            ## write the outside spending overview

            other_year = None
            if cycle == '2016':
                other_year = '2014'
            elif cycle == '2014':
                other_year = '2016'
            cycle_list = [cycle_fake(cycle, "/overview/outside-money/%s/" % cycle), cycle_fake(other_year, "/overview/outside-money/%s/" % other_year)]


            page_title = "Independent Expenditures, %s Cycle" % cycle    
            c = Context({"update_time": update_time, "sums": summary_obj, "page_title":page_title, "cycle_list":cycle_list, "cycle_start":CYCLE_START, "cycle_end":CYCLE_END})
            this_template = get_template('generated_pages/overview_outside_money.html')
            result = this_template.render(c)
            thisurl = "/overview/outside-money/%s/" % cycle
            
            thisflatpage, created = FlatPage.objects.get_or_create(url=thisurl)            
            thisflatpage.title = page_title
            thisflatpage.content = result
            thisflatpage.template_name = "flatpages/cycle_enabled_base.html" # Default for admin flatpages too
            if not thisflatpage.sites.all():
                thisflatpage.sites.add(this_site)
                
            thisflatpage.save()
            
            
            ### end outside spending part. 

            
            ## deal with the inside spending
        
            # assumes fake committees have been removed; disregard joint fundraisers which disburse their proceeds to their recipients
            
            print "Running main overview summaries" 
            
            all_webk = WebK.objects.filter(cycle=cycle).exclude(com_des='J')
            summary_types = [
                {'name':'Super PACs', 'code':'UOVW', 'outside_spending': summary_obj['super_pacs']},
                {'name':'Party Committees', 'code':'XYZ', 'outside_spending': summary_obj['party_committees']},
                {'name':'House Candidate Committees', 'code':'H', 'outside_spending': summary_obj['house_committees']},
                {'name':'Senate Candidate Committees', 'code':'S', 'outside_spending': summary_obj['senate_committees']},
                {'name':'Other PACs', 'code':'NQ', 'outside_spending': summary_obj['oth_committees']}
            ]
            for s in summary_types:
                code_list = [i for i in s['code']]
                sums = all_webk.filter(com_typ__in=code_list).aggregate(tot_rec=Sum('tot_rec'), tot_dis=Sum('tot_dis'), par_com_con=Sum('par_com_con'), oth_com_con=Sum('oth_com_con'), ind_ite_con=Sum('ind_ite_con'), ind_uni_con=Sum('ind_uni_con'), fed_can_com_con=Sum('fed_can_com_con'), tot_ope_exp=Sum('tot_ope_exp'), ope_exp=Sum('ope_exp'))
                s['tot_dis'] = sums['tot_dis'] or 0
                s['tot_rec'] = sums['tot_rec'] or 0
                s['oth_com_con'] = (sums['oth_com_con'] or 0) + (sums['par_com_con'] or 0)
                s['ind_ite_con']= sums['ind_ite_con'] or 0
                s['ind_uni_con'] = sums['ind_uni_con'] or 0
                s['fed_can_com_con'] = sums['fed_can_com_con'] or 0
            
                # operating expenses are recorded differently for candidate pacs
                if s['code'] in ['H', 'S']:
                    s['tot_ope_exp'] = sums['ope_exp'] or 0
                else: 
                    s['tot_ope_exp'] = sums['tot_ope_exp'] or 0
        
        
            ## reuse this stuff as is in noncommittees
            all_noncommittees = Committee_Overlay.objects.filter(ctype__in=['I'], cycle=cycle).exclude(designation='J')       
            sums = all_noncommittees.aggregate(tot_ie=Sum('total_indy_expenditures'))
            ##
            dark_money_total_ies = sums['tot_ie']
            summary_types.append({'name':'Dark Money', 'code':'I', 'outside_spending': sums['tot_ie'], 'tot_dis':0, 'tot_rec':0, 'oth_com_con':0, 'ind_ite_con':0, 'ind_uni_con':0, 'fed_can_com_con':0, 'tot_ope_exp':0})
        
            print "\toverview main sums: %s" % summary_obj
            print "\toverview inside money: %s" % summary_types


            other_year = None
            if cycle == '2016':
                other_year = '2014'
            elif cycle == '2014':
                other_year = '2016'
            cycle_list = [cycle_fake(cycle, "/overview/%s/" % cycle), cycle_fake(other_year, "/overview/%s/" % other_year)]



            page_title = "Cycle Overview, %s Cycle" % cycle    
            c = Context({"update_time": update_time, "sums": summary_obj, "inside_money": summary_types, "page_title":page_title, "cycle_list":cycle_list, "cycle_start":CYCLE_START, "cycle_end":CYCLE_END})
            
            this_template = get_template('generated_pages/overview_main.html')
            result = this_template.render(c)
            
            thisurl = "/overview/%s/" % cycle
            
            thisflatpage, created = FlatPage.objects.get_or_create(url=thisurl)            
            thisflatpage.title = page_title
            thisflatpage.content = result
            thisflatpage.template_name = "flatpages/cycle_enabled_base.html" # Default for admin flatpages too
            if not thisflatpage.sites.all():
                thisflatpage.sites.add(this_site)

                
            thisflatpage.save()
        
        
            # now superpacs
            print "Now running superpac summaries... "
            
            sp_summary_types = [
                {'name':'Super PACs', 'code':'UO'},
                {'name':'Hybrid Super PACs', 'code':'VW'},
                {'name': 'All Super PACs', 'code':'UOVW'}
            ]
            all_superpacs = Committee_Overlay.objects.filter(cycle=cycle,ctype__in=['U', 'O', 'V', 'W']).exclude(designation='J')
        
            for s in sp_summary_types:
                code_list = [i for i in s['code']]
                sums = all_superpacs.filter(ctype__in=code_list).aggregate(tot_ie=Sum('total_indy_expenditures'), tot_rec=Sum('total_receipts'), coh=Sum('cash_on_hand'))
                s['tot_ie'] = sums['tot_ie'] or 0
                s['tot_rec'] = sums['tot_rec'] or 0
                s['coh'] = sums['coh'] or 0
        
        
            top_superpacs = all_superpacs.order_by('-total_indy_expenditures')[:20]
            
            page_title = "Top Super PACs by Independent Expenditures, %s Cycle" % (cycle)
            
            
            other_year = None
            if cycle == '2016':
                other_year = '2014'
            elif cycle == '2014':
                other_year = '2016'
            cycle_list = [cycle_fake(cycle, "/overview/super-pacs/%s/" % cycle), cycle_fake(other_year, "/overview/super-pacs/%s/" % other_year)]
            
            c = Context({"update_time": update_time, "sums": sp_summary_types, "top_superpacs": top_superpacs, "page_title":page_title, "cycle_list":cycle_list, "cycle_start":CYCLE_START, "cycle_end":CYCLE_END})
            this_template = get_template('generated_pages/overview_superpac.html')
            result = this_template.render(c)
        
            thisurl = "/overview/super-pacs/%s/" % cycle
            
            thisflatpage, created = FlatPage.objects.get_or_create(url=thisurl)            
            thisflatpage.title = page_title
            thisflatpage.content = result
            thisflatpage.template_name = "flatpages/cycle_enabled_base.html" # Default for admin flatpages too
            if not thisflatpage.sites.all():
                thisflatpage.sites.add(this_site)

                
            thisflatpage.save()
                
        
            print "Regenerating dark money pages"
            # now dark money groups -- the sums were calculated previously 


            top_noncommittees = all_noncommittees.order_by('-total_indy_expenditures')[:10]
        
            page_title = "Top Dark Money groups by Independent Expenditures, %s Cycle" % (cycle)
            
            other_year = None
            if cycle == '2016':
                other_year = '2014'
            elif cycle == '2014':
                other_year = '2016'
            cycle_list = [cycle_fake(cycle, "/overview/dark-money/%s/" % cycle), cycle_fake(other_year, "/overview/dark-money/%s/" % other_year)]
            
            
            c = Context({"update_time": update_time, "dark_money_total_ies": dark_money_total_ies, "top_darkmoneyers": top_noncommittees, "page_title":page_title, "cycle_list":cycle_list, "cycle_start":CYCLE_START, "cycle_end":CYCLE_END})
            this_template = get_template('generated_pages/overview_dark_money.html')
            result = this_template.render(c)
            
            thisurl = "/overview/dark-money/%s/" % cycle

            thisflatpage, created = FlatPage.objects.get_or_create(url=thisurl)            
            thisflatpage.title = page_title
            thisflatpage.content = result
            thisflatpage.template_name = "flatpages/cycle_enabled_base.html" # Default for admin flatpages too
            if not thisflatpage.sites.all():
                thisflatpage.sites.add(this_site)


            thisflatpage.save()
            
            
            
            ## do connected pacs now.
        
            all_webk = WebK.objects.filter(cycle=cycle).exclude(com_des='J')

            connected_org_types = [
                {'name':'Corporation', 'code':'C'},
                {'name':'Labor organization', 'code':'L'},
                {'name':'Member Organization', 'code':'M'},
                {'name':'Cooperative', 'code':'V'},
                {'name':'Trade Association', 'code':'T'},
                {'name':'Corporation without capital stock', 'code':'W'}
            ]

            for j in connected_org_types:
                committees = Committee.objects.filter(cmte_tp__in=['N', 'Q'], cycle=str(cycle),org_tp=j['code'])
                committee_id_list = [i.cmte_id for i in committees]

                sums = all_webk.filter(com_id__in=committee_id_list).aggregate(tot_rec=Sum('tot_rec'), tot_dis=Sum('tot_dis'), par_com_con=Sum('par_com_con'), oth_com_con=Sum('oth_com_con'), ind_ite_con=Sum('ind_ite_con'), ind_uni_con=Sum('ind_uni_con'), fed_can_com_con=Sum('fed_can_com_con'), tot_ope_exp=Sum('tot_ope_exp'), ope_exp=Sum('ope_exp'))
                j['tot_dis'] = sums['tot_dis'] or 0
                j['tot_rec'] = sums['tot_rec'] or 0
                j['oth_com_con'] = (sums['oth_com_con'] or 0) + (sums['par_com_con'] or 0)
                j['ind_ite_con']= sums['ind_ite_con'] or 0
                j['ind_uni_con'] = sums['ind_uni_con'] or 0
                j['fed_can_com_con'] = sums['fed_can_com_con'] or 0
                j['tot_ope_exp'] = sums['tot_ope_exp'] or 0
         
            print "building connected pac with inside money set to %s" % (connected_org_types)
            
            page_title = "Cycle Overview, %s Cycle -- Connected pacs" % cycle
            other_year = None
            if cycle == '2016':
                other_year = '2014'
            elif cycle == '2014':
                other_year = '2016'
            cycle_list = [cycle_fake(cycle, "/overview/connected/%s/" % cycle), cycle_fake(other_year, "/overview/connected/%s/" % other_year)]
            
            
            c = Context({"update_time": update_time, "inside_money": connected_org_types, "page_title":page_title, "cycle_list":cycle_list, "cycle_start":CYCLE_START, "cycle_end":CYCLE_END})
            this_template = get_template('generated_pages/overview_connected.html')
            result = this_template.render(c)
            thisurl = "/overview/connected/%s/" % cycle
            
            thisflatpage, created = FlatPage.objects.get_or_create(url=thisurl)            
            thisflatpage.title = page_title
            thisflatpage.content = result
            thisflatpage.template_name = "flatpages/cycle_enabled_base.html" # Default for admin flatpages too
            if not thisflatpage.sites.all():
                thisflatpage.sites.add(this_site)


            thisflatpage.save()
        
            
        
        