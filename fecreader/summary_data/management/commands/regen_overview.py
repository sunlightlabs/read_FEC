## godawful mess to redo some static pages. Best if this process doesn't live too long. 

from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Sum
from django.core.management.base import BaseCommand, CommandError


from formdata.models import SkedE
from summary_data.models import Committee_Overlay
from fec_alerts.models import WebK

PROJECT_ROOT = settings.PROJECT_ROOT


CYCLE_START = date(2013,1,1)

class Command(BaseCommand):
    help = "Regenerate the main static overview page."
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
        update_time = datetime.now()
        
        print "summaries"
        summary_obj = {}
        
        all_independent_expenditures = SkedE.objects.filter(superceded_by_amendment=False, expenditure_date_formatted__gte=CYCLE_START)
        summary_obj['ie_sum'] = all_independent_expenditures.aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
        print "positive vs negative"
        # postive vs negative
        summary_obj['positive'] = all_independent_expenditures.filter(support_oppose_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['negative'] = all_independent_expenditures.filter(support_oppose_checked='O').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']

        print "target party breakdown"
        # breakdown by target party
        summary_obj['pro_dem'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['pro_rep'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['anti_dem'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['anti_rep'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
        print "office breakdown"
        # breakdown by target party
        summary_obj['senate'] = all_independent_expenditures.filter(candidate_office_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['house'] = all_independent_expenditures.filter(candidate_office_checked='H').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
       
        
        all_outside_spenders = Committee_Overlay.nulls_last_objects.filter(total_indy_expenditures__gt=0)
        print "outside spending types"
        # breakdown by types:
        summary_obj['party_committees'] = all_outside_spenders.filter(ctype__in=('X', 'Y', 'Z')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        # includes hybrids
        summary_obj['super_pacs'] = all_outside_spenders.filter(ctype__in=('O', 'U', 'V', 'W')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        # non-committees:
        summary_obj['non_committees'] = all_outside_spenders.filter(ctype__in=('I')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['oth_committees'] = all_outside_spenders.filter(ctype__in=('N', 'Q')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['house_committees'] = all_outside_spenders.filter(ctype__in=('H')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['senate_committees'] = all_outside_spenders.filter(ctype__in=('S')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        
        
        print "outside spending parties"
        # breakdown by parties 
        summary_obj['dem_affil'] = all_outside_spenders.filter(political_orientation='D').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['rep_affil'] = all_outside_spenders.filter(political_orientation='R').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['no_affil'] = all_outside_spenders.exclude(political_orientation__in=('R', 'D')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        ## write the outside spending overview
                
        c = Context({"update_time": update_time, "sums": summary_obj})
        this_template = get_template('generated_pages/overview_outside_money.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_outside_money_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()
        
        ## deal with the inside spending
        
        # assumes fake committees have been removed
        all_webk = WebK.objects.filter(cycle='2014')
        summary_types = [
            {'name':'Super PACs', 'code':'UOVW', 'outside_spending': summary_obj['super_pacs']},
            {'name':'Party Committees', 'code':'XYZ', 'outside_spending': summary_obj['party_committees']},
            {'name':'House Candidate Committees', 'code':'H', 'outside_spending': summary_obj['house_committees']},
            {'name':'Senate Candidate Committees', 'code':'S', 'outside_spending': summary_obj['senate_committees']},
            {'name':'Non-connected PACs', 'code':'NQ', 'outside_spending': summary_obj['oth_committees']}
        ]
        for s in summary_types:
            code_list = [i for i in s['code']]
            sums = all_webk.filter(com_typ__in=code_list).aggregate(tot_rec=Sum('tot_rec'), tot_dis=Sum('tot_dis'), par_com_con=Sum('par_com_con'), oth_com_con=Sum('oth_com_con'), ind_ite_con=Sum('ind_ite_con'), ind_uni_con=Sum('ind_uni_con'), fed_can_com_con=Sum('fed_can_com_con'), tot_ope_exp=Sum('tot_ope_exp'), ope_exp=Sum('ope_exp'))
            s['tot_dis'] = sums['tot_dis']
            s['tot_rec'] = sums['tot_rec']
            s['oth_com_con'] = sums['oth_com_con'] + sums['par_com_con']
            s['ind_ite_con']= sums['ind_ite_con']
            s['ind_uni_con'] = sums['ind_uni_con']
            s['fed_can_com_con'] = sums['fed_can_com_con']
            
            # operating expenses are recorded differently for candidate pacs
            if s['code'] in ['H', 'S']:
                s['tot_ope_exp'] = sums['ope_exp']
            else:
                s['tot_ope_exp'] = sums['tot_ope_exp']
        
        
        ## reuse this stuff as is in noncommittees
        all_noncommittees = Committee_Overlay.objects.filter(ctype__in=['I'])        
        sums = all_noncommittees.aggregate(tot_ie=Sum('total_indy_expenditures'))
        ##
        dark_money_total_ies = sums['tot_ie']
        summary_types.append({'name':'Dark Money', 'code':'I', 'outside_spending': sums['tot_ie'], 'tot_dis':0, 'tot_rec':0, 'oth_com_con':0, 'ind_ite_con':0, 'ind_uni_con':0, 'fed_can_com_con':0, 'tot_ope_exp':0})
        
        print "overview main sums: %s" % summary_obj
        print "overview inside money: %s" % summary_types

        c = Context({"update_time": update_time, "sums": summary_obj, "inside_money": summary_types})
        this_template = get_template('generated_pages/overview_main.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_main_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()
        
        # now superpacs
        
        sp_summary_types = [
            {'name':'Super PACs', 'code':'UO'},
            {'name':'Hybrid Super PACs', 'code':'VW'},
            {'name': 'All Super PACs', 'code':'UOVW'}
        ]
        all_superpacs = Committee_Overlay.objects.filter(ctype__in=['U', 'O', 'V', 'W'])
        
        for s in sp_summary_types:
            code_list = [i for i in s['code']]
            sums = all_superpacs.filter(ctype__in=code_list).aggregate(tot_ie=Sum('total_indy_expenditures'), tot_rec=Sum('total_receipts'), coh=Sum('cash_on_hand'))
            s['tot_ie'] = sums['tot_ie']
            s['tot_rec'] = sums['tot_rec']
            s['coh'] = sums['coh']
        
        
        top_superpacs = all_superpacs.order_by('-total_indy_expenditures')[:50]
        
        c = Context({"update_time": update_time, "sums": sp_summary_types, "top_superpacs": top_superpacs})
        this_template = get_template('generated_pages/overview_superpac.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_superpac_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()
        
        print "Regenerating dark money pages"
        # now dark money groups -- the sums were calculated previously 


        top_noncommittees = all_noncommittees.order_by('-total_indy_expenditures')[:50]
        
        c = Context({"update_time": update_time, "sums": dark_money_total_ies, "dark_money_total_ies": top_noncommittees})
        this_template = get_template('generated_pages/overview_dark_money.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_dark_money_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()

        