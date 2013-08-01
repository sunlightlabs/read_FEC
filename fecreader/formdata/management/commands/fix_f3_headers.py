

from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY

from formdata.models import Filing_Header
from fec_alerts.models import new_filing
from formdata.utils.filing_processors import process_filing_header

from parsing.filerange import filerange


# load up a form parser
fp = form_parser()

# have standardized F3, F3X, F3P in sourcesalt directory. 
def process_f3_header(header_data):
    return_dict = {}
    return_dict['coh_end'] = header_data.get('col_a_cash_on_hand_close_of_period')
    return_dict['tot_raised'] = header_data.get('col_a_total_receipts')
    return_dict['tot_spent'] = header_data.get('col_a_total_disbursements')
    return_dict['new_loans'] = header_data.get('col_a_total_loans')
    return return_dict

class Command(BaseCommand):
    help = "Reparse the F3 filing headers b/c of a bug in the sources csv"
    requires_model_validation = False

    def handle(self, *args, **options):
        
        filing_headers = Filing_Header.objects.filter(form='F3')
        for fh in filing_headers:
            print "Processing filing %s" % (fh.filing_number)
            f1 = filing(fh.filing_number)
            form = f1.get_form_type()
            version = f1.get_version()
            

            header = f1.get_first_row()
            header_line = fp.parse_form_line(header, version)
            fh.header_data=header_line
            fh.save()
            
            try:
                this_filing = new_filing.objects.get(filing_number = fh.filing_number)
            
                parsed_data = process_f3_header(header_line)
                #print "got data %s" % (parsed_data)
                
                this_filing.coh_end =  parsed_data['coh_end'] if parsed_data['coh_end'] else None
                this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else None
                this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else None
                this_filing.new_loans = parsed_data['new_loans'] if parsed_data['new_loans'] else None
                this_filing.save()
            
            except new_filing.DoesNotExist:
                print "new_filing MISSING FOR %s" % (new_filing.filing_number)
                continue
            
            
# still need to move the corrected totals into the fh data, and the newfiling data...

        