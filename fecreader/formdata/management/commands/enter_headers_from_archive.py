# Requires the date is specified in filerange.py -- so we give the header a filed date. 

### THIS IS OUT OF DATE B/C HEADERS NOW GO ONLY IN NEW_FILING!!! 

from os import system, path

from dateutil.parser import parse as dateparse
from datetime import date, timedelta, datetime

from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY

from formdata.models import Filing_Header
from formdata.utils.filing_processors import process_filing_header

from parsing.filerange import filerange



# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Enter file headers; don't mark them as either amended or not."
    requires_model_validation = False

    def handle(self, *args, **options):
        start_date = date(2013,6,16)
        end_date = date(2013,6,18)
        one_day = timedelta(days=1)
        
        
        this_date = start_date
        while (this_date < end_date):
            datestring = this_date.strftime("%Y%m%d")
            entry_time = datetime(this_date.year, this_date.month, this_date.day, 7,0)
            print "datestring %s" % (datestring)
            this_date += one_day            
            filing_info = None
            try:
                filing_info = filerange[datestring]
            except KeyError:
                print "Missing data for %s" % datestring
                continue
            
            #print filing_info
            thisfilerange=range(int(filing_info['first']), 1+int(filing_info['last']))
            #thisfilerange=['868338']
            for filenum in thisfilerange:
                
                # see if the file is downloaded, and if it isn't just ignore it. Some numbers are skipped; our assumption here is that we're entering files that have come from a zipfile. 
                
                local_file_location = FILECACHE_DIRECTORY + "/" + str(filenum) + ".fec"
                if path.isfile(local_file_location):
                    print "Processing %s" % (filenum)
                    process_filing_header(filenum, fp=fp, filing_time=entry_time, filing_time_is_exact=False)
                else:
                    print "!! missing file %s" % filenum
