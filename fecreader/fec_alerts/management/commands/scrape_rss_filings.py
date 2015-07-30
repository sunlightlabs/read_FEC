import urllib2
import re
import datetime

import pytz

from lxml import etree
from StringIO import StringIO

from urllib import urlencode
from optparse import make_option
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError

from fec_alerts.models import new_filing,  Filing_Scrape_Time
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, CYCLE
from fec_alerts.utils.fec_logging import fec_logger
from summary_data.utils.update_utils import set_update
from django.conf import settings
from shared_utils.cycle_utils import get_cycle_from_date

FILING_SCRAPE_KEY = settings.FILING_SCRAPE_KEY
my_logger=fec_logger()
date_re = "<dc:date>(.*?)</dc:date>"
data_re = "\*\*CommitteeId:\s*([C\d]*)\s*\|\s*FilingId:\s*(\d*)\s*\|\s*FormType:\s*([\d\w]*)\s*\|\s*CoverageFrom:\s*([\d\-]*?)\s\|\s*CoverageThrough:\s*([\d\-]*?)\s\|"
name_re = "<title>New filing by\s*(.*?)\s*</title>"

est=pytz.timezone('US/Eastern')


def get_local_time(utc_time):
    
    return utc_time.astimezone(est).replace(tzinfo=None)

def enter_filing(data_hash):

    filing_created=False
    related_committee = None
    
    try:
        thisobj = new_filing.objects.get(filing_number=data_hash['filing_number'])
        try:
            thisobj.filed_date
        except AttributeError:
            
            try:
                thisobj.filed_date = get_local_time(data_hash['filed_date'])
                thisobj.process_time = get_local_time(data_hash['filed_date'])
                thisobj.save()
            except pytz.exceptions.AmbiguousTimeError:
                thisobj.filed_date = data_hash['filed_date']
                thisobj.process_time = data_hash['filed_date']
                thisobj.save()
                
        
        
    except new_filing.DoesNotExist:
        print "entering %s %s" % (data_hash['filing_number'], data_hash['committee_id'])
        is_superpac=False
        
        try:
            thisobj = new_filing.objects.create(
                is_superpac = is_superpac,
                #related_committee = related_committee,
                fec_id = data_hash['committee_id'],
                committee_name = data_hash['committee_name'],
                filing_number = data_hash['filing_number'],
                form_type = data_hash['form_type'],
                filed_date = get_local_time(data_hash['filed_date']),
                process_time = get_local_time(data_hash['filed_date']),
            )
        except pytz.exceptions.AmbiguousTimeError:
            thisobj = new_filing.objects.create(
                is_superpac = is_superpac,
                #related_committee = related_committee,
                fec_id = data_hash['committee_id'],
                committee_name = data_hash['committee_name'],
                filing_number = data_hash['filing_number'],
                form_type = data_hash['form_type'],
                filed_date = data_hash['filed_date'],
                process_time = data_hash['filed_date'],
            )
        
        filing_created=True
        needs_saving=False
        try:
            thisobj.coverage_from_date = data_hash['coverage_from_date']
            thisobj.cycle = get_cycle_from_date(data_hash['coverage_from_date'])
            needs_saving=True
        except KeyError:
            pass
        try:
            thisobj.coverage_to_date = data_hash['coverage_to_date']
            needs_saving=True
        except KeyError:
            pass
        
        
        
        if needs_saving:
            thisobj.save()
    
    # return true if a new filing was created
    return filing_created

def parse_xml_from_text(xml):
    tree = etree.parse(StringIO(xml))
    results = []
    print tree
    
    for  elt in tree.getiterator('item'):
        stringtext =  etree.tostring(elt, pretty_print=True)
        #print stringtext
        result_hash={}
        
        name_found = re.search(name_re, stringtext)
        name = name_found.group(1)        
        
        date_found = re.search(date_re, stringtext)
        date = date_found.group(1)
        date_parsed = dateparse(date)
        
        data_found = re.search(data_re, stringtext)
        
        result_hash={
            'committee_id':data_found.group(1),
            'committee_name':name,
            'filing_number':data_found.group(2),
            'form_type':data_found.group(3),
            'filed_date':date_parsed,
        }    
        
        
        coverage_from = data_found.group(4)
        coverage_to = data_found.group(5)
        coverage_from_date = None
        coverage_to_date = None
        if (coverage_from != ''):
            result_hash['coverage_from_date'] = dateparse(coverage_from)
        if (coverage_to != ''):
            result_hash['coverage_to_date'] = dateparse(coverage_to)
        
        results.append(result_hash)
    return results

class Command(BaseCommand):
    """  Creates new_filing objects from RSS feed. Will set cycle if possible. """
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        new_filings = 0
        # old URL
        #rss_url = "http://query.nictusa.com/rss/newfilings.rss"
        # This was moved here, approximately 9/21/12
        #rss_url = "http://fecapps.nictusa.com/rss/generate?preDefinedFilingType=ALL"
        rss_url = "http://efilingapps.fec.gov/rss/generate?preDefinedFilingType=ALL"
        
        my_logger.info('SCRAPE_DAILY_FILINGS - starting regular run')
        headers = {'User-Agent': USER_AGENT}   
        data = None       
        req = urllib2.Request(rss_url, data, headers)
        response = urllib2.urlopen(req)
        rssdata = response.read()
        
        #print rssdata
        results = parse_xml_from_text(rssdata)
        for result in results:
            filing_entered = enter_filing(result)
            if filing_entered:
                new_filings += 1
        
        now = Filing_Scrape_Time.objects.create()
        my_logger.info("SCRAPE_DAILY_FILINGS - completing regular run--created %s new filings" % new_filings)
        set_update('scrape_electronic_filings')
        
        
