from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from formdata.models import Filing_Header
from fec_alerts.models import new_filing
from summary_data.utils.party_reference import get_party_from_pty
from ftpdata.models import Committee
from summary_data.models import Committee_Overlay


# have standardized F3, F3X, F3P in sourcesalt directory. 
def process_f3_header(header_data):
    return_dict = {}
    return_dict['coh_end'] = header_data.get('col_a_cash_on_hand_close_of_period')
    return_dict['tot_raised'] = header_data.get('col_a_total_receipts')
    return_dict['tot_spent'] = header_data.get('col_a_total_disbursements')
    return_dict['new_loans'] = header_data.get('col_a_total_loans')
    return return_dict
    
class Command(BaseCommand):
    help = "Set data fields in the new filing from the parsed Filing_Header"
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        new_filings_to_process = new_filing.objects.filter(previous_amendments_processed=False,header_is_processed=True).order_by('filing_number')
        #new_filings_to_process = new_filing.objects.filter(form_type__startswith='F3').order_by('filing_number')
        for this_filing in new_filings_to_process:
            print "processing %s " % (this_filing.filing_number)
            
            try:
                co = Committee_Overlay.objects.get(fec_id=this_filing.fec_id)
                this_filing.committee_designation = co.designation
                this_filing.committee_type = co.ctype
                this_filing.committee_slug = co.slug
                this_filing.party = co.party
                
            except Committee_Overlay.DoesNotExist:
                try:
                    co = Committee.objects.get(cmte_id=this_filing.fec_id, cycle=2014)
                    this_filing.committee_designation = co.cmte_dsgn
                    this_filing.committee_type = co.cmte_tp
                    this_filing.party = get_party_from_pty(co.cmte_pty_affiliation)
                
                except Committee.DoesNotExist:
                    pass
                    
            
            try:
                header = Filing_Header.objects.get(filing_number = this_filing.filing_number)
            except Filing_Header.DoesNotExist:
                print "FILING_HEADER MISSING FOR %s" % (this_filing.filing_number)
                continue
            header_data = header.header_data
            
            form_type = this_filing.form_type
            parsed_data = {'coh_start':None, 'coh_end':None, 'new_loans':None,'tot_raised':None,'tot_spent':None}
            
            if form_type in ['F3XA', 'F3XN', 'F3XT', 'F3A', 'F3N', 'F3T','F3PA', 'F3PN', 'F3PT', 'F3', 'F3X']:
                parsed_data = process_f3_header(header_data)
                #print "got data %s" % (parsed_data)
                
                this_filing.coh_end =  parsed_data['coh_end'] if parsed_data['coh_end'] else None
                this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else None
                this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else None
                this_filing.new_loans = parsed_data['new_loans'] if parsed_data['new_loans'] else None
                this_filing.save()
            