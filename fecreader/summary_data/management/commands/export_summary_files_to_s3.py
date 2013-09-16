from boto.s3.connection import S3Connection
from boto.s3.key import Key

import time, os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from summary_data.utils.update_utils import set_update
from summary_data.utils.summary_utils import write_all_candidates

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY =  getattr(settings, 'AWS_SECRET_ACCESS_KEY')
CSV_EXPORT_DIR =  getattr(settings, 'CSV_EXPORT_DIR')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BULK_EXPORT_PATH = getattr(settings, 'AWS_BULK_EXPORT_PATH')
SUMMARY_EXPORT_KEY = getattr(settings, 'SUMMARY_EXPORT_KEY')



class Command(BaseCommand):
    help = "Dump the big files to a predefined spot in the filesystem. They need to then get moved to S3"
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
         
        
        conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
        
        filename = "candidates.csv" 
        
        local_file = "%s/%s" % (CSV_EXPORT_DIR, filename)
        print "Dumping %s to %s" % ('candidate summary', local_file)
        write_all_candidates(local_file)
        
        # need to gzip these
        gzip_cmd = "gzip -f %s" % (local_file)
        filename_zipped = filename + ".gz"
        local_file_zipped = local_file + ".gz"
        # old style os.system just works - subprocess sucks. 
        proc = os.system(gzip_cmd)
        
        s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename_zipped)
        print "pushing %s to S3: bucket=%s path=%s" % (local_file_zipped, AWS_STORAGE_BUCKET_NAME,s3_path)
        start = time.time()
        k = Key(b)
        k.key = s3_path
        k.set_contents_from_filename(local_file_zipped, policy='public-read')
        elapsed_time = time.time() - start
        print "elapsed time for pushing to s3 is %s" % (elapsed_time)
            
        
        # if we didn't die, set the update time
        set_update(SUMMARY_EXPORT_KEY)
