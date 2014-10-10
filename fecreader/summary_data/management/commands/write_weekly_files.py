# write some files 

import csv 

from datetime import datetime, date

from django.conf import settings
from django.db.models import Sum
from django.core.management.base import BaseCommand, CommandError


from formdata.models import SkedE
from summary_data.models import Committee_Overlay
from datetime import date
from summary_data.utils.weekly_update_utils import get_week_number, get_week_end, summarize_week_queryset

CHART_CSV_DOWNLOAD_DIR = settings.CHART_CSV_DOWNLOAD_DIR
CSV_FILE_NAME = 'weekly_ies.csv'


data_start = date(2013,1,1)


def make_header(start_week_number, end_week_number):
    headers = ['data_id','data_series_name']
    for week in range(start_week_number, end_week_number + 1):
        headers.append(get_week_end(week).strftime("%m/%d/%Y"))
    return headers


## some queries to help define sets
all_ies = SkedE.objects.filter(superceded_by_amendment=False)

superpacs = Committee_Overlay.objects.filter(ctype__in=['U', 'O'], total_indy_expenditures__gt=0)
superpac_id_list = [i.fec_id for i in superpacs]

party_committees = Committee_Overlay.objects.filter(ctype__in=['X', 'Y', 'Z'], total_indy_expenditures__gt=0)
party_committee_id_list = [i.fec_id for i in party_committees]


data_series = [
    {'data_id':1,'data_series_name':'All Independent Expenditures', 'q':all_ies},
    {'data_id':2,'data_series_name':'Dark Money', 'q':all_ies.filter(filer_committee_id_number__startswith='C9')},
    {'data_id':3,'data_series_name':'Super PACs', 'q':all_ies.filter(filer_committee_id_number__in=superpac_id_list)},
    {'data_id':4,'data_series_name':'Party Committees', 'q':all_ies.filter(filer_committee_id_number__in=party_committee_id_list)},
]

class Command(BaseCommand):
    help = "Write some data csvs"
    requires_model_validation = False
   
    
    def handle(self, *args, **options):
        today = date.today()
        last_week = get_week_number(today) - 1
        first_week = get_week_number(data_start)
        
        outf = "%s/%s" % (CHART_CSV_DOWNLOAD_DIR, CSV_FILE_NAME)
        print "writing to %s" % outf
        outfile = open(outf, 'w')
        field_names = make_header(first_week, last_week)
        outfile.write(",".join(field_names) +"\n")

        dw = csv.writer(outfile)
        
        for data in data_series:
            this_row = [data['data_id'], data['data_series_name']]
            for week in range(first_week, last_week+1):
                print "handling %s week %s" % (data['data_series_name'], week)
                this_row.append(summarize_week_queryset(week, data['q']))
            dw.writerow(this_row)



        
