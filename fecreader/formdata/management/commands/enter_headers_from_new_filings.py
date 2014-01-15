from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY

from fec_alerts.models import new_filing

#from formdata.models import Filing_Header
from fec_alerts.utils.filing_processors import process_new_filing




# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Enter file headers; don't mark them as either amended or not."
    requires_model_validation = False

    def handle(self, *args, **options):
        downloaded_filings = new_filing.objects.filter(filing_is_downloaded=True, header_is_processed=False).order_by('filing_number')
        for filing in downloaded_filings:
            print "Entering filing %s, entry_time %s" % (filing.filing_number, filing.process_time)
            result_header = None
            try: 
                result_header = process_new_filing(filing, fp=fp, filing_time=filing.process_time, filing_time_is_exact=True)
            ## It seems like the FEC's response is now to give a page not found response instead of a 500 error or something. The result is that the except no longer seems to apply. 
            except IOError:
                # if the file's missing, keep running. 
                print "MISSING FILING: %s" % (filing.filing_number)  
                continue
            if result_header:
                filing.header_is_processed=True
                filing.save()
            else:
                print "Header not created right... %s" % (filing)