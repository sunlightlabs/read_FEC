# set the downloaded status of files purportedly missing of it's somehow gotten borked, not that that has ever happened... 

from django.core.management.base import BaseCommand, CommandError

from parsing.read_FEC_settings import FILECACHE_DIRECTORY, FEC_DOWNLOAD

from fec_alerts.models import new_filing
from os import path



class Command(BaseCommand):
    help = "Download files from FTP. Mark them as having been downloaded."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        new_filings = new_filing.objects.all().order_by('filing_number')
        for filing in new_filings:
            local_location = FILECACHE_DIRECTORY + "/" + str(filing.filing_number) + ".fec"
            
            if path.isfile(local_location):
                filing.filing_is_downloaded=True
                filing.save()
                print "Found file %s" % filing.filing_number
            else:
                print "Couldn't find file %s" % filing.filing_number
                filing.filing_is_downloaded=False
                filing.save()