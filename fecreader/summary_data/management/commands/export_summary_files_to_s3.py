from boto.s3.connection import S3Connection
from boto.s3.key import Key

import time, os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from summary_data.utils.update_utils import set_update
from summary_data.utils.summary_utils import write_all_candidates, write_all_webks

from formdata.utils.dump_utils import dump_big_contribs, dump_big_non_indiv_contribs

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY =  getattr(settings, 'AWS_SECRET_ACCESS_KEY')
CSV_EXPORT_DIR =  getattr(settings, 'CSV_EXPORT_DIR')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BULK_EXPORT_PATH = getattr(settings, 'AWS_BULK_EXPORT_PATH')
SUMMARY_EXPORT_KEY = getattr(settings, 'SUMMARY_EXPORT_KEY')

def push_to_s3(local_file_zipped, AWS_STORAGE_BUCKET_NAME, s3_path):
    
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)

    start = time.time()
    k = Key(b)
    k.key = s3_path
    k.set_contents_from_filename(local_file_zipped, policy='public-read')
    elapsed_time = time.time() - start
    print "elapsed time for pushing to s3 is %s" % (elapsed_time)


class Command(BaseCommand):
    help = "Dump the big files to a predefined spot in the filesystem. They need to then get moved to S3"
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
        
        filename = "candidates.csv" 
        webk_filename = "all_webk.csv"
        contrib_filename = 'superpac_contribs.csv'
        nonindiv_contrib_filename = 'nonindiv_nonpac_superpac_contribs.csv'
        
        local_file = "%s/%s" % (CSV_EXPORT_DIR, filename)
        local_webk_file = "%s/%s" % (CSV_EXPORT_DIR, webk_filename)
        local_contrib_file = "%s/%s" % (CSV_EXPORT_DIR, contrib_filename)
        local_nonindiv_contrib_file = "%s/%s" % (CSV_EXPORT_DIR, nonindiv_contrib_filename)
        
        
        dump_big_non_indiv_contribs(local_nonindiv_contrib_file)
        write_all_candidates(local_file)
        write_all_webks(local_webk_file)
        dump_big_contribs(local_contrib_file)
        
        
        # need to gzip these
        gzip_cmd = "gzip -f %s %s %s %s" % (local_file, local_webk_file, local_contrib_file, local_nonindiv_contrib_file)
        filename_zipped = filename + ".gz"
        filename_webk_zipped = webk_filename + ".gz"
        filename_contrib_zipped = contrib_filename + ".gz"
        filename_nonindiv_contrib_zipped = nonindiv_contrib_filename + ".gz"
        
        local_file_zipped = local_file + ".gz"
        local_webk_file_zipped = local_webk_file + ".gz"
        local_contrib_file_zipped = local_contrib_file + ".gz"
        local_nonindiv_contrib_file_zipped = local_nonindiv_contrib_file + ".gz"
        
        
        # old style os.system just works - subprocess sucks. 
        proc = os.system(gzip_cmd)
        s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename_zipped)
        webk_s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename_webk_zipped)
        contrib_s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename_contrib_zipped)
        nonindiv_s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename_nonindiv_contrib_zipped)
        
        push_to_s3(local_file_zipped, AWS_STORAGE_BUCKET_NAME, s3_path)
        push_to_s3(local_webk_file_zipped, AWS_STORAGE_BUCKET_NAME, webk_s3_path)
        push_to_s3(local_contrib_file_zipped, AWS_STORAGE_BUCKET_NAME, contrib_s3_path)
        push_to_s3(local_nonindiv_contrib_file_zipped, AWS_STORAGE_BUCKET_NAME, nonindiv_s3_path)

        
        # if we didn't die, set the update time
        set_update(SUMMARY_EXPORT_KEY)
