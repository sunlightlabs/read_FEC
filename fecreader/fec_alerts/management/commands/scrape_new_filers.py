
import re
import requests
import urllib
from time import sleep
import lxml.html
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand

from fec_alerts.models import newCommittee

# url is: http://www.fec.gov/press/press2011/new_form1dt.shtml
# local copy saved as http://www.fec.gov/press/press2011/new_form1dt.shtml



def clean_entry(htmlbit):   
    if htmlbit:
        htmlbit = htmlbit.strip()
        htmlbit = htmlbit.upper()
    return htmlbit

def addCommittee(fec_id, ctype, name, date_filed):
    obj, created = newCommittee.objects.get_or_create(fec_id=fec_id, 
                            defaults={'ctype':ctype, 'name':name, 'date_filed':date_filed})
    return created

def scrape_page():
    url ="http://www.fec.gov/press/press2011/new_form1dt.shtml"
    
    response = requests.request("GET", url)
    assert response.status_code == 200, 'Unable to retrieve {0}, method {1}, status {2}'.format(url, method, response.status_code)
    rawhtml = response.content


    #print rawhtml
    doc = lxml.html.fromstring(rawhtml)
    table = doc.cssselect('table')[0]
    rows = table.cssselect('tr')

    # skip header row and final row ()
    for row in rows[1:]:
        try:
            count, cid, ctype, name, raw_date = [clean_entry(x.text_content()) for x in row.getchildren()]
            file_date = dateparse(raw_date)

            new = addCommittee(cid, ctype, name, file_date)
            if new:
                print "added: %s, %s, %s, %s" % (cid, ctype, name, file_date)
        except ValueError:
            print "Couldn't parse line: %s" % row.text_content()
            pass
            
class Command(BaseCommand): 
    def handle(self, *args, **options):
        print "Scraping the FEC press offices new committee page"
        scrape_page()