from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum



from summary_data.utils.summary_utils import summarize_committee_periodic_webk, summarize_committee_periodic_electronic
from summary_data.models import Candidate_Overlay, Candidate_Time_Summary, Authorized_Candidate_Committees, Committee_Time_Summary

class Command(BaseCommand):
    help = "Redo the summaries of *all candidates* - not just those that need it"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        candidates = Candidate_Overlay.objects.all()
        
        ## Eventually should use all authorized candidates, but right now there's a ton of junk in there--this needs serious manual cleaning before we can run these. Also, open question: what if an authorized committee doesn't file on the same schedule? 
        for candidate in candidates:
            candidate_pcc = candidate.pcc
            
            authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate.fec_id).values('committee_id')
            committee_list = [x.get('committee_id') for x in authorized_committee_list]
            
            print "For candidate %s entering from list: %s" % (candidate.name, committee_list)
            all_summaries = Committee_Time_Summary.objects.filter(com_id__in=committee_list, coverage_from_date__gte=(date(2012,12,31))).order_by('-coverage_through_date', '-coverage_from_date')
            
            
            if all_summaries:
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
                
                
                # get data for all reports
                sums = all_summaries.aggregate(tot_contrib=Sum('tot_contrib'), tot_disburse=Sum('tot_disburse'), tot_receipts=Sum('tot_receipts'), tot_non_ite_contrib=Sum('tot_non_ite_contrib'))
                
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
            