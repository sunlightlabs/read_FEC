# dump csv files of roi analysis

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import time, os, csv

from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay, Pac_Candidate, Committee_Overlay, roi_pair
from django.conf import settings

from summary_data.management.commands.export_summary_files_to_s3 import push_to_s3

cycle_start = date(2013,1,1)

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY =  getattr(settings, 'AWS_SECRET_ACCESS_KEY')
CSV_EXPORT_DIR =  getattr(settings, 'CSV_EXPORT_DIR')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BULK_EXPORT_PATH = getattr(settings, 'AWS_BULK_EXPORT_PATH')
SUMMARY_EXPORT_KEY = getattr(settings, 'SUMMARY_EXPORT_KEY')



class Command(BaseCommand):
    help = "Write ROI files"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        update_time = datetime.now()
        # write ROI of all outside spenders
        data_disclaimer = "This file was last generated at %s" % (update_time)
        header_row = ['fec_id', 'name', 'ctype', 'designation', 'total_outside_spending', 'political_leaning', 'main_activity', 'roi', 'support_winners', 'oppose_losers', 'support_losers', 'oppose_winners', 'support_unclassified', 'oppose_unclassified', 'ie_support_dems', 'ie_oppose_dems', 'ie_support_reps', 'ie_oppose_reps']
        
        filename = 'roi.csv'
        local_roi_file = "%s/%s" % (CSV_EXPORT_DIR, filename)
        print "writing to %s" % local_roi_file
        roi_file = open(local_roi_file, 'w')
        writer = csv.writer(roi_file)
        writer.writerow([data_disclaimer])
        writer.writerow(header_row)
        
        outside_spenders = Committee_Overlay.objects.filter(total_indy_expenditures__gt=0).order_by('-total_indy_expenditures')
        for os in outside_spenders:
            writer.writerow([os.fec_id, os.name, os.ctype, os.designation, os.total_indy_expenditures, os.political_orientation, os.major_activity(),os.roi, os.support_winners, os.oppose_losers, os.support_losers, os.oppose_winners, os.support_unclassified, os.oppose_unclassified, os.ie_support_dems, os.ie_oppose_dems, os.ie_support_reps, os.ie_oppose_reps])
        
        roi_file.close()
        
        s3_path = "%s/%s" % (AWS_BULK_EXPORT_PATH,filename)
        push_to_s3(local_roi_file, AWS_STORAGE_BUCKET_NAME, s3_path)
        print "pushing to: %s/%s" % (AWS_STORAGE_BUCKET_NAME, s3_path)
        
        
        
        
