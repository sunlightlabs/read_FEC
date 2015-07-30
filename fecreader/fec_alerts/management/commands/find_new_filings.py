# look for new filings by just testing filing numbers. This is a hack to deal with the fact that
# the feed is too slow. 

import urllib2
from time import sleep
from django.utils import timezone
import pytz
from datetime import date


from django.core.management.base import BaseCommand, CommandError
from fec_alerts.models import new_filing


from parsing.read_FEC_settings import FILECACHE_DIRECTORY, FEC_DOWNLOAD
from summary_data.utils.update_utils import set_update
from django.conf import settings


FILING_SCRAPE_KEY = settings.FILING_SCRAPE_KEY

est = pytz.timezone('US/Eastern')

def get_date(datetime):
    this_datetime = datetime.astimezone(est)
    return date(this_datetime.year, this_datetime.month, this_datetime.day)

class Command(BaseCommand):
    help = "Download files from FTP. Mark them as having been downloaded."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        
        highest_filing_number = new_filing.objects.all().order_by('-filing_number')[0].filing_number
        print "highest previously available filing number: %s" % (highest_filing_number)
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
                    now = timezone.now()
                    thisobj = new_filing.objects.create(
                                filing_number = trial_file_number, 
                                process_time = now,
                                filed_date = get_date(now))
                                

            except urllib2.HTTPError:
                print "didn't find %s" % (location)
                file_misses += 1
                
            if file_misses >= file_miss_threshold:
                break
                
            sleep(1)
        
        # set the update time. 
        set_update('scrape_electronic_filings')
        
        
        

