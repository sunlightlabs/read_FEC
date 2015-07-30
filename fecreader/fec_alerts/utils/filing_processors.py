from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from fec_alerts.models import new_filing
from fec_alerts.utils.form_mappers import *
from shared_utils.cycle_utils import get_cycle_from_date


from django.db import connection, transaction


verbose = True
cursor = connection.cursor()

""" These routines are no longer used. 
def exec_raw_sql(cmd_list):
    for cmd in cmd_list:
        try:
            print "running cmd <<<%s>>>" % cmd
            cursor.execute(cmd)
            status = cursor.statusmessage
            if status:
                print "STATUS: %s" % status
        except IntegrityError:
            print "Integrity Error!!!"


def mark_superceded_body_rows(header_row):
    print "Marking superceded body rows"
    SkedA.objects.filter(header=header_row, superceded_by_amendment=False).update(superceded_by_amendment=True)
    SkedB.objects.filter(header=header_row, superceded_by_amendment=False).update(superceded_by_amendment=True)
    SkedE.objects.filter(header=header_row, superceded_by_amendment=False).update(superceded_by_amendment=True)
    OtherLine.objects.filter(header=header_row, superceded_by_amendment=False).update(superceded_by_amendment=True)


def mark_superceded_amendment_header_rows(header_row):
    print "marking superceded amendment header rows"
    try:
        original = Filing_Header.objects.get(filing_number=header_row.amends_filing, is_superceded=False)
        #print "Writing amended original: %s %s" % (original.filing_number, header.filing_number)
        original.is_superceded=True
        original.amended_by = header.filing_number
        original.save()
        # mark child rows as amended
        mark_superceded_body_rows(original)
        
    except Filing_Header.DoesNotExist:
        pass
        

    # Now find others that amend the same filing 
    earlier_amendments = Filing_Header.objects.filter(is_amendment=True,amends_filing=header_row.amends_filing, filing_number__lt=header_row.filing_number, is_superceded=False)
    
    for earlier_amendment in earlier_amendments:
        #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
        earlier_amendment.is_superceded=True
        earlier_amendment.amended_by = header_row.filing_number
        earlier_amendment.save()
        # 
        mark_superceded_body_rows(earlier_amendment)
        

"""

def process_new_filing(thisnewfiling, fp=None, filing_time=None, filing_time_is_exact=False):
    """ Enter the file header if needed.  """
       
    if not fp:
        fp = form_parser()
        
    #print "Processing filing %s" % (filingnum)
    f1 = filing(thisnewfiling.filing_number)
    if f1.get_error():
        return False
        
    form = f1.get_form_type()
    version = f1.get_version()

    ## leave the form if it's already been entered-- that's where it says if it is terminated. 
    if not thisnewfiling.form_type:
        thisnewfiling.form_type = form
        
    # check if it's an amendment based on form types -- if so, mark it. Otherwise the F1's will look like they haven't been amended. 
    try:
        if thisnewfiling.form_type[-1].upper() == 'A':
            thisnewfiling.is_amendment = True
    except IndexError:
        pass

    # only parse forms that we're set up to read
    if not fp.is_allowed_form(form):
        if verbose:
            print "Not a parseable form: %s - %s" % (form, thisnewfiling.filing_number)
        
        if thisnewfiling.is_amendment:
            thisnewfiling.save()
        return True

    header = f1.get_first_row()
    header_line = fp.parse_form_line(header, version)

    amended_filing=None
    if f1.is_amendment:
        amended_filing = f1.headers['filing_amended']


    
    from_date = None
    through_date = None
    #print "header line is: %s " % header_line
    try:
        # dateparse('') will give today, oddly
        if header_line['coverage_from_date']:
            from_date = dateparse(header_line['coverage_from_date'])
            if from_date:
                thisnewfiling.cycle = get_cycle_from_date(from_date)
    except KeyError:
        print "problem with coverage_from_date"
        pass
        
    try:                
        if header_line['coverage_through_date']:
            through_date = dateparse(header_line['coverage_through_date'])
            if through_date:
                thisnewfiling.cycle = get_cycle_from_date(through_date)
    except KeyError:
        print "coverage_through_date"
        pass

    
    # Create the filing -- but don't mark it as being complete. 
    

    
    
    
    thisnewfiling.fec_id = f1.headers['fec_id']
    thisnewfiling.coverage_from_date = from_date
    thisnewfiling.coverage_to_date = through_date
    thisnewfiling.is_amendment = f1.is_amendment
    thisnewfiling.amends_filing = amended_filing
    thisnewfiling.amendment_number = f1.headers['report_number'] or None
    thisnewfiling.header_data = header_line
    
    print thisnewfiling.__dict__

    thisnewfiling.save()
    
    return True

