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
            
            all_summaries = Committee_Time_Summary.objects.filter(com_id=candidate_pcc, coverage_from_date__gte=(date(2012,12,31))).order_by('-coverage_from_date')
            
            
            if all_summaries:
                most_recent_report = all_summaries[0]
                
                # Independent expenditures are summarized separately. 
                candidate.cash_on_hand_date = most_recent_report.coverage_through_date
                candidate.cash_on_hand = most_recent_report.cash_on_hand_end
                candidate.outstanding_loans = most_recent_report.outstanding_loans
                
                sums = all_summaries.aggregate(tot_contrib=Sum('tot_contrib'), tot_disburse=Sum('tot_disburse'), tot_receipts=Sum('tot_receipts'), tot_non_ite_contrib=Sum('tot_non_ite_contrib'))
                
                candidate.total_contributions = sums['tot_contrib']
                candidate.total_unitemized = sums['tot_non_ite_contrib']
                candidate.total_disbursements = sums['tot_disburse']
                candidate.total_receipts = sums['tot_receipts']
                
                if not candidate.has_contributions and candidate.total_contributions > 0:
                    candidate.has_contributions = True
                

                candidate.save()
            