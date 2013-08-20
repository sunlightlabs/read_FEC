from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum



from summary_data.utils.summary_utils import summarize_committee_periodic_webk, summarize_committee_periodic_electronic, summarize_noncommittee_periodic_electronic
from summary_data.models import Committee_Overlay, Committee_Time_Summary

class Command(BaseCommand):
    help = "Redo the summaries of *all committees* - not just those that need it"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        #all_committees = Committee_Overlay.objects.all()
        all_committees = Committee_Overlay.objects.filter(ctype='I')
        for committee in all_committees:
            print "Handling %s" % (committee.fec_id)

            if committee.is_paper_filer:
                summarize_committee_periodic_webk(committee.fec_id, force_update=True)
            else:
                # if they file on F5's it's different since, the same form is used for monthly and daily reports
                if committee.ctype == 'I':
                    summarize_noncommittee_periodic_electronic(committee.fec_id, force_update=True)                    
                else:
                    summarize_committee_periodic_electronic(committee.fec_id, force_update=True)
                
            
            ## Now that the data is summarized, update the committee_overlay. At the moment we're just looking at the two year cycle; for senate races older webk files need to be populated. Senate special elections complicte this a little; e.g. Hawaii senate race being held off cycle. 
            
            ## we need to log the gaps somewhere. 
            
            all_summaries = Committee_Time_Summary.objects.filter(com_id=committee.fec_id, coverage_from_date__gte=(date(2012,12,31))).order_by('-coverage_from_date')
            
            if all_summaries:
                most_recent_report = all_summaries[0]
                
                # Independent expenditures are summarized separately. 
                committee.cash_on_hand_date = most_recent_report.coverage_through_date
                committee.cash_on_hand = most_recent_report.cash_on_hand_end
                committee.outstanding_loans = most_recent_report.outstanding_loans
                
                sums = all_summaries.aggregate(tot_contrib=Sum('tot_contrib'), tot_disburse=Sum('tot_disburse'), tot_non_ite_contrib=Sum('tot_non_ite_contrib'), tot_receipts=Sum('tot_receipts'), coo_exp_par=Sum('coo_exp_par'))
                
                committee.total_contributions = sums['tot_contrib']
                committee.total_disbursements = sums['tot_disburse']
                committee.total_unitemized = sums['tot_non_ite_contrib']
                committee.total_coordinated_expenditures = sums['coo_exp_par']
                committee.total_receipts = sums['tot_receipts']
                
                if not committee.has_contributions and committee.total_contributions > 0:
                    committee.has_contributions = True
                # coordinated expenditures can only be done by party committees so:
                if committee.ctype in ['Y', 'Z'] and not committee.has_coordinated_expenditures and committee.total_coordinated_expenditures > 0:
                    committee.has_coordinated_expenditures = True
                
                committee.save()
                    
            
            