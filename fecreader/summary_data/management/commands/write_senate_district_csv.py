# one off to dump senate races as a csv; probably want a general solution to this, but... 

import csv 

from datetime import datetime, date

from django.conf import settings
from django.db.models import Sum
from django.core.management.base import BaseCommand, CommandError


from formdata.models import SkedE
from summary_data.models import DistrictWeekly
from datetime import date
from summary_data.utils.weekly_update_utils import get_week_number, get_week_end

CHART_CSV_DOWNLOAD_DIR = settings.CHART_CSV_DOWNLOAD_DIR
CSV_FILE_NAME = 'competitive_senate_seats_weekly.csv'


data_start = date(2014,6,1)

# 
senate_districts = [
    {'state':'NC', 'id':1034},
    {'state':'MI', 'id':1025},
    {'state':'AR', 'id':986},
    {'state':'NH', 'id':1040},
    {'state':'CO', 'id':992},
    {'state':'LA', 'id':1016},
    {'state':'KS', 'id':1012},
    {'state':'AK', 'id':982},
    {'state':'IA', 'id':1004}
]

district_list=[]
for i in senate_districts:
    district_list.append(i['id'])

def make_header(start_week_number, end_week_number):
    headers = ['state','district_id']
    for week in range(start_week_number, end_week_number + 1):
        headers.append(get_week_end(week).strftime("%m/%d/%Y"))
    return headers

class Command(BaseCommand):
    help = "Regenerate the main static overview page."
    requires_model_validation = False
   
    
    def handle(self, *args, **options):
        today = date.today()
        last_week = get_week_number(today) - 1
        first_week = get_week_number(data_start)
        
        outf = "%s/%s" % (CHART_CSV_DOWNLOAD_DIR, CSV_FILE_NAME)
        outfile = open(outf, 'w')
        field_names = make_header(first_week, last_week)
        outfile.write(",".join(field_names) +"\n")

        dw = csv.writer(outfile)
        
        
        summaries = DistrictWeekly.objects.filter(cycle_week_number__gte=first_week, cycle_week_number__lte=last_week, district__pk__in=district_list).select_related('District')
        summary_hash = {}
        for s in summaries:
            summary_hash["%s-%s" % (s.district.pk, s.cycle_week_number)] = s.outside_spending
        
        # regroup by week
        for i in senate_districts:
            row = [i['state'], i['id']]
            for week in range(first_week, last_week+1):
                key = "%s-%s" % (i['id'], week)
                try:
                    row.append(summary_hash[key])
                except KeyError:
                    row.append(0)
            dw.writerow(row)
            
        