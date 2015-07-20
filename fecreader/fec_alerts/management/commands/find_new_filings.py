# look for new filings by just testing filing numbers. This is a hack to deal with the fact that
# the feed is too slow. 

import urllib2
from time import sleep
from django.utils import timezone
import pytz


from django.core.management.base import BaseCommand, CommandError
from fec_alerts.models import new_filing


from parsing.read_FEC_settings import FILECACHE_DIRECTORY, FEC_DOWNLOAD

# to be new settings

TEMP_DOWNLOAD_DIR = "/"


class Command(BaseCommand):
    help = "Download files from FTP. Mark them as having been downloaded."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        """
        location = FEC_DOWNLOAD % (1200000)
        print location
        result = urllib2.urlopen(location)
        size = int(result.headers["Content-Length"])
        print "%s, %s" % (location, trial_file_number, size)
        """
        
        # highest_filing_number = new_filing.objects.all().order_by('-filing_number')[0].filing_number
        highest_filing_number = 1015679
        trial_file_number = highest_filing_number
        highest_available_file_number = highest_filing_number
        file_misses = 0
        file_miss_threshold = 3
        
        while True:
            trial_file_number += 1 
            location = FEC_DOWNLOAD % (trial_file_number)
            print location
            try:
                result = urllib2.urlopen(location)
                print "Found %s" % (location)
                try:
                    new_filing.objects.get(filing_number = trial_file_number)
                except new_filing.DoesNotExist:
                    thisobj = new_filing.objects.create(
                                filing_number = trial_file_number, 
                                process_time = timezone.now())
                                

            except urllib2.HTTPError:
                print "didn't find %s" % (location)
                file_misses += 1
                
            if file_misses >= file_miss_threshold:
                break
                
            sleep(1)
        
        

