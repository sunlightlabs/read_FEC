from datetime import date
from django.core.management.base import BaseCommand, CommandError 
from django.db.models import Sum

from django.template import Template
from django.template.loader import get_template
from django.template import Context

election_day_2014 = date(2014,11,4)
cycle_start = date(2013,1,1)

from summary_data.models import *
from formdata.models import SkedE

# HOW MANY SHOULD WE DISPLAY? 
SPENDER_COUNT = 10

CANDIDATE_DISPLAY_THRESHOLD = 50000

def supporting_opposing(support_oppose_code):
    support = ''
    if support_oppose_code == 'S':
        support='Support'
    elif support_oppose_code == 'O':
        support = 'Oppose'    
    return support






    
class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        outside_spenders = Committee_Overlay.objects.filter(total_indy_expenditures__gte=50000)
        primary_ies = SkedE.objects.filter(superceded_by_amendment=False, expenditure_date__gte=cycle_start, election_code__in=['P2014', 'R2014'])
        
        # first pull the top outside spenders by amount spent in primaries or runoffs
        spender_list = []
        for outside_spender in outside_spenders:
            #print "processing %s" % (outside_spender)
            
            their_ies = primary_ies.filter(filer_committee_id_number=outside_spender.fec_id)
            
            total = their_ies.aggregate(tot_ies=Sum('expenditure_amount'))['tot_ies']
            oppose_dems = their_ies.filter(candidate_party_checked='D', support_oppose_checked='O').aggregate(tot_ies=Sum('expenditure_amount'))['tot_ies']
            oppose_reps = their_ies.filter(candidate_party_checked='R', support_oppose_checked='O').aggregate(tot_ies=Sum('expenditure_amount'))['tot_ies']
            support_dems = their_ies.filter(candidate_party_checked='D', support_oppose_checked='S').aggregate(tot_ies=Sum('expenditure_amount'))['tot_ies']
            support_reps = their_ies.filter(candidate_party_checked='R', support_oppose_checked='S').aggregate(tot_ies=Sum('expenditure_amount'))['tot_ies']
            
            this_spender_data = {'name':outside_spender.name, 'url':outside_spender.get_absolute_url(), 'total_ies':total, 'oppose_dems':oppose_dems, 'oppose_reps':oppose_reps, 'support_dems':support_dems, 'support_reps':support_reps, 'type':outside_spender.display_type(), 'orientation':outside_spender.display_political_orientation(), 'ie_url':outside_spender.get_filtered_ie_url(), 'fec_id':outside_spender.fec_id}
            #print this_spender_data
            spender_list.append(this_spender_data)
        
        # sort the list by outside spending in the primary
        spender_list.sort(key=lambda x: x['total_ies'], reverse=True)
        
        top_spenders = spender_list[:SPENDER_COUNT]
        #print "top ten spenders"
        #print spender_list[:10]
        
        # Now add the top candidates supported or opposed in the primary by each of those groups. 
        spender_data = []
        
        for outside_spender in top_spenders:
            their_ies = primary_ies.filter(filer_committee_id_number=outside_spender['fec_id']).order_by('candidate_id_checked', 'support_oppose_checked')
            candidate_summary = their_ies.values('candidate_id_checked', 'support_oppose_checked').annotate(Sum('expenditure_amount'))
            candidate_list=[]
            for candidate in candidate_summary:
                
                if candidate['expenditure_amount__sum'] >= CANDIDATE_DISPLAY_THRESHOLD:
                    c = Candidate_Overlay.objects.get(fec_id=candidate['candidate_id_checked'])
                
                    candidate_list.append({'name':c.name, 'url':c.get_absolute_url(), 'incumbent':c.is_incumbent, 'party':c.display_party(), 'office':c.detailed_office(), 'support_oppose':supporting_opposing(candidate['support_oppose_checked']), 'amount':candidate['expenditure_amount__sum'], 'result':c.show_candidate_status()})
                
            candidate_list.sort(key=lambda x: x['amount'], reverse=True)
            outside_spender['candidates'] = candidate_list
            spender_data.append(outside_spender)
        
        ##print "spender_data"
        #print spender_data

        # now write it out to screen via a template
        this_template = get_template('generated_pages/primary_chart.html')
        c = Context({'spenders':spender_data})
        result = this_template.render(c)
        print result
                
                
                
            
            
        