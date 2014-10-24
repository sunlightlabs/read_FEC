## total hack to query non-django table for itemized superpac donors over time. Must update table before running this...

# write some files 

import csv 

from datetime import datetime, date

from django.conf import settings
from django.db.models import Sum
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from datetime import date
from summary_data.utils.weekly_update_utils import get_week_number, get_week_end, get_week_start

CHART_CSV_DOWNLOAD_DIR = settings.CHART_CSV_DOWNLOAD_DIR
CSV_FILE_NAME = 'weekly_superpac_donations.csv'
CSV_FILE_NAME_CUMULATIVE = 'weekly_superpac_donations_cumulative.csv'



data_start = date(2013,1,1)
start = data_start.strftime("%Y-%m-%d")

write_cumulative = False

def make_header(start_week_number, end_week_number):
    headers = ['data_id','data_series_name']
    for week in range(start_week_number, end_week_number + 1):
        headers.append(get_week_end(week).strftime("%m/%d/%Y"))
    return headers

data_series = [
    {'data_id':0,'data_series_name':'All Itemized Super PAC contributions', 'q':""},
    {'data_id':1,'data_series_name':'Democratic Super PAC contributions', 'q':" and political_orientation = 'D'"},
    {'data_id':2,'data_series_name':'Republican Super PAC contributions', 'q':" and political_orientation = 'R'"}
]

# select sum(contribution_amount) from superpac_donors where contribution_date_formatted >= '%s' and contribution_date_formatted <= '%s' and upper(line_type) = SA11AI and political_orientation = 'D';

# select sum(contribution_amount) from superpac_donors where contribution_date_formatted >= '2014-09-24' and contribution_date_formatted <= '2014-09-30' and upper(line_type) = SA11AI and political_orientation = 'D';

def summarize_week_cumulative(week_number, and_condition, cursor):
    week_end = get_week_end(week_number).strftime("%Y-%m-%d")
    
    query = "select sum(contribution_amount) from superpac_donors where contribution_date_formatted >= '%s' and contribution_date_formatted <= '%s' and upper(line_type) = 'SA11AI' %s" % (start, week_end, and_condition)
    print "query is: %s" % query
    
    cursor.execute(query)
    row = cursor.fetchone()
    value = row[0]
    return value or 0

def summarize_week(week_number, and_condition, cursor):
    week_start = get_week_start(week_number).strftime("%Y-%m-%d")
    week_end = get_week_end(week_number).strftime("%Y-%m-%d")

    query = "select sum(contribution_amount) from superpac_donors where contribution_date_formatted >= '%s' and contribution_date_formatted <= '%s' and upper(line_type) = 'SA11AI' %s" % (week_start, week_end, and_condition)
    print "query is: %s" % query

    cursor.execute(query)
    row = cursor.fetchone()
    value = row[0]
    return value or 0

class Command(BaseCommand):
    help = "Write some data csvs"
    requires_model_validation = False
   
    
    def handle(self, *args, **options):
        cursor = connection.cursor()
        today = date.today()
        last_week = get_week_number(today) - 1
        first_week = get_week_number(data_start)
        
        
        outf = "%s/%s" % (CHART_CSV_DOWNLOAD_DIR, CSV_FILE_NAME)
        print "writing to %s" % outf
        outfile = open(outf, 'w')
        field_names = make_header(first_week, last_week)
        outfile.write(",".join(field_names) +"\n")
        dw = csv.writer(outfile)


        if write_cumulative:

            outcumf = "%s/%s" % (CHART_CSV_DOWNLOAD_DIR, CSV_FILE_NAME_CUMULATIVE) 
            print "writing cumulative numbers to %s" % outcumf
            outcumfile = open(outcumf, 'w')
            cum_field_names = make_header(1, last_week)
            outcumfile.write(",".join(cum_field_names) +"\n")
            cumdw = csv.writer(outcumfile)
        
        for data in data_series:
            this_row = [data['data_id'], data['data_series_name']]
            this_cum_row = [data['data_id'], data['data_series_name']]
            for week in range(first_week, last_week+1):
                print "handling %s week %s" % (data['data_series_name'], week)
                this_row.append(summarize_week(week, data['q'], cursor))
                if write_cumulative:
                    this_cum_row.append(summarize_week_cumulative(week, data['q'], cursor))
            dw.writerow(this_row)
            if write_cumulative:
                cumdw.writerow(this_cum_row)
            


        
