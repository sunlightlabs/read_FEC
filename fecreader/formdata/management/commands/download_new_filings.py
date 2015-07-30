import subprocess
from time import sleep
from os import path

from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, FEC_DOWNLOAD

from fec_alerts.models import new_filing




class Command(BaseCommand):
    help = "Download files from FTP. Mark them as having been downloaded."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        new_filings = new_filing.objects.filter(filing_is_downloaded=False, header_is_processed=False).order_by('filing_number')
        for filing in new_filings:
            if filing.filing_number < 1015680:
                continue
            print "need to handle %s" % (filing.filing_number)
            location = FEC_DOWNLOAD % (filing.filing_number)
            local_location = FILECACHE_DIRECTORY + "/" + str(filing.filing_number) + ".fec"
            cmd = "curl \"%s\" -o %s" % (location, local_location)
            print "Running command %s" % (cmd)
            # run it from a curl shell
            proc = subprocess.Popen(cmd,shell=True)
            # if it's there when we're done, mark it as downloaded


            print "Now sleeping for 1 second"
            sleep(1)
            
            # Putting the file check after the 1 second sleep gives better results; sometimes it appears absent if it's not before
            if path.isfile(local_location):
                print "File %s is there" % (filing.filing_number)
                filing.filing_is_downloaded=True
                filing.save()
            else:
                print "MISSING: %s" % (filing.filing_number)
            

            