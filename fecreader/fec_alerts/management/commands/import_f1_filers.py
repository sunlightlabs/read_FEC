# import data from the new f1 filers csv. This replaces an older FEC one-off page of new filers.

import csv
from decimal import *
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand
from parsing.read_FEC_settings import FTP_DATA_DIR, CYCLE
from fec_alerts.models import f1filer
from summary_data.utils.overlay_utils import make_committee_from_f1filer


two_digit_cycle = "16"
#override
CYCLE = 2016


def readfile(filelocation):
    fh = open(filelocation, 'r')
    reader = csv.DictReader(fh)
    count = 0
    for row in reader:
        try:
            thiscom = f1filer.objects.get(cmte_id=row['cmte_id'], cycle=CYCLE)
        except f1filer.DoesNotExist:
            print "Creating %s %s" % (row['cmte_id'], row['cmte_nm'])
            # first create the f1filer object:
            row['cycle'] = '2014'
            row['receipt_dt'] = dateparse(row['receipt_dt'])
            try:
                del row[None]
            except KeyError:
                pass
                
            print row
            thisf1 = f1filer(**row)
            thisf1.save()
            
            ## if we are creating a new f1, check if it's a committee and if not, create one. 
            make_committee_from_f1filer(row['cmte_id'], cycle)


class Command(BaseCommand): 
    def handle(self, *args, **options):
        print "load f1 filers"
        filename =  "/%s/Form1Filer_%s.csv" % (two_digit_cycle, two_digit_cycle)
        filelocation = FTP_DATA_DIR + filename
        readfile(filelocation)
