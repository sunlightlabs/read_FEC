# import data from the new f1 filers csv. This replaces an older FEC one-off page of new filers.

import csv
from decimal import *
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand
from parsing.read_FEC_settings import FTP_DATA_DIR, CYCLE
from fec_alerts.models import f1filer
from summary_data.utils.overlay_utils import make_committee_from_f1filer
from summary_data.utils.update_utils import set_update

from django.conf import settings

COMMITTEES_SCRAPE_KEY  = settings.COMMITTEES_SCRAPE_KEY

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'

two_digit_cycle = CURRENT_CYCLE[2:4]


""" FEC 'update' means new file headers. Grr.  """
def transform_column_headers(new_row):
    return  {
        'cmte_id': new_row['COMMITTEE_ID'],
        'cmte_nm': new_row['COMMITTEE_NAME'],
        'cmte_st1': new_row['COMMITTEE_STREET_1'],
        'cmte_st2': new_row['COMMITTEE_STREET_2'],
        'cmte_city': new_row['COMMITTEE_CITY'],
        'cmte_st': new_row['COMMITTEE_STATE'],
        'cmte_zip': new_row['COMMITTEE_ZIP'],
        'affiliated_cmte_nm': new_row['AFFILIATED_COMMITTEE_NAME'],
        'filed_cmte_tp': new_row['FILED_COMMITTEE_TYPE'],
        'filed_cmte_dsgn': new_row['FILED_COMMITTEE_DESIGNATION'],
        'filing_freq': new_row['FILING_FREQUENCY'],
        'org_tp': new_row['ORGANIZATION_TYPE'],
        'tres_nm': new_row['TREASURER_NAME'],
        'receipt_dt': new_row['RECEIPT_DATE'],
        'cmte_email': new_row['COMMITTEE_EMAIL'],
        'cmte_web_url': new_row['COMMITTEE_WEB_URL'],
        'begin_image_num': new_row['BEGIN_IMAGE_NUMBER']
    }


def readfile(filelocation):
    fh = open(filelocation, 'r')
    reader = csv.DictReader(fh)
    count = 0
    for newstyle_row in reader:
        row = transform_column_headers(newstyle_row)
        try:
            thiscom = f1filer.objects.get(cmte_id=row['cmte_id'])
        except f1filer.DoesNotExist:
            print "Creating %s %s" % (row['cmte_id'], row['cmte_nm'])
            # first create the f1filer object:
            row['cycle'] = str(CYCLE)
            try:
                row['receipt_dt'] = dateparse(row['receipt_dt'])
            except:
                print "can't parse original receipt date='%s', skipping" % (row['receipt_dt'])
                continue
            
            try:
                del row[None]
            except KeyError:
                pass
                
            print row
            thisf1 = f1filer(**row)
            thisf1.save()
            
            ## if we are creating a new f1, check if it's a committee and if not, create one. 
            make_committee_from_f1filer(row['cmte_id'], row['cycle'])


class Command(BaseCommand): 
    def handle(self, *args, **options):
        print "load f1 filers"
        filename =  "/%s/Form1Filer_%s.csv" % (two_digit_cycle, two_digit_cycle)
        filelocation = FTP_DATA_DIR + filename
        readfile(filelocation)
        set_update(COMMITTEES_SCRAPE_KEY)
