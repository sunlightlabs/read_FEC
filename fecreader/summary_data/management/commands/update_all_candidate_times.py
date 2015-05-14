from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum



from summary_data.utils.summary_utils import summarize_committee_periodic_webk
from summary_data.models import Candidate_Overlay, Authorized_Candidate_Committees, Committee_Time_Summary, Committee_Overlay
from shared_utils.cycle_utils import cycle_calendar
from django.conf import settings


try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'

this_cycle_calendar = cycle_calendar[int(CURRENT_CYCLE)]
this_cycle_start = this_cycle_calendar['start']
this_cycle_end = this_cycle_calendar['end']
    
class Command(BaseCommand):
    help = "Redo the summaries of *all candidates* - not just those that need it"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        candidates = Candidate_Overlay.objects.filter(cycle=CURRENT_CYCLE)
        
        
        for candidate in candidates:
            candidate_pcc = candidate.pcc
            
            authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate.fec_id, cycle=CURRENT_CYCLE).values('committee_id')
            
            committee_list = [x.get('committee_id') for x in authorized_committee_list]
            
            print "For candidate %s entering from list: %s" % (candidate.name, committee_list)
            all_summaries = Committee_Time_Summary.objects.filter(com_id__in=committee_list, coverage_from_date__gte=this_cycle_start, coverage_through_date__lte=this_cycle_end).order_by('-coverage_through_date', '-coverage_from_date')
            
            
            if all_summaries:
                ## Get most recent data from the time summary reports. But for totals that include recent stuff, use committee summaries.
                
                most_recent_report = all_summaries[0]
                
                recent_reports = all_summaries.filter(coverage_from_date=most_recent_report.coverage_from_date, coverage_through_date=most_recent_report.coverage_through_date)
                
                # get data from the most recent report
                recent_sums = recent_reports.aggregate( outstanding_loans=Sum('outstanding_loans'), cash_on_hand_end=Sum('cash_on_hand_end'))
                for i in recent_sums:
                    if not recent_sums[i]:
                        recent_sums[i] = 0
                # Independent expenditures are summarized separately. 
                candidate.cash_on_hand_date = most_recent_report.coverage_through_date
                candidate.cash_on_hand = recent_sums['cash_on_hand_end']
                candidate.outstanding_loans = recent_sums['outstanding_loans']
                
            
            authorized_committees = Committee_Overlay.objects.filter(fec_id__in=committee_list,cycle=CURRENT_CYCLE)
            sums = authorized_committees.aggregate(tot_contrib=Sum('total_contributions'), tot_disburse=Sum('total_disbursements'), tot_receipts=Sum('total_receipts'), tot_non_ite_contrib=Sum('total_unitemized'))
            
            
            for i in sums:
                if not sums[i]:
                    sums[i] = 0
            
            candidate.total_contributions = sums['tot_contrib']
            candidate.total_unitemized = sums['tot_non_ite_contrib']
            candidate.total_disbursements = sums['tot_disburse']
            candidate.total_receipts = sums['tot_receipts']
            
            if not candidate.has_contributions and candidate.total_contributions > 0:
                candidate.has_contributions = True
            
            candidate.save()
        