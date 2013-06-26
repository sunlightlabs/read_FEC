from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.models import Filing_Header, Committee_Changed
from formdata.utils.write_csv_to_db import CSV_dumper
from formdata.utils.form_mappers import *

from django.db import connection, transaction


verbose = True
cursor = connection.cursor()


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
        



def process_filing_header(filingnum, fp=None, filing_time=None, filing_time_is_exact=False):
    """ Enter the file header if needed.  """
    
    header_needs_entry = True
    this_filing_header = None
    
    # enter it if we don't have it already:
    try:    
        this_filing_header = Filing_Header.objects.get(filing_number=filingnum)
        print "Header already entered! %s" % (filingnum)
        header_needs_entry = False
        rows_need_entry = not this_filing_header.entry_complete
        print "Rows need entry: %s" % rows_need_entry
        
    except Filing_Header.DoesNotExist:
        pass
    
    if not header_needs_entry:
        return True
    
    
    
    if not fp:
        fp = form_parser()
        
    #print "Processing filing %s" % (filingnum)
    f1 = filing(filingnum)
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        if verbose:
            print "Not a parseable form: %s - %s" % (form, filingnum)

        return True

    header = f1.get_first_row()
    header_line = fp.parse_form_line(header, version)

    amended_filing=None
    if f1.is_amendment:
        amended_filing = f1.headers['filing_amended']


    try:
        Committee_Changed.objects.get_or_create(committee_id=f1.headers['fec_id'])
    except Committee_Changed.MultipleObjectsReturned:
        pass
    
    from_date = None
    through_date = None
    try:
        # dateparse('') will give today, oddly
        if header_line['coverage_from_date']:
            from_date = dateparse(header_line['coverage_from_date'])
        if header_line['coverage_through_date']:
            through_date = dateparse(header_line['coverage_through_date'])
    except KeyError:
        pass
    
    # Create the filing -- but don't mark it as being complete. 
    this_filing_header = Filing_Header(
        raw_filer_id=f1.headers['fec_id'],
        form=form,
        filing_number=filingnum,
        version=f1.version,
        coverage_from_date=from_date,
        coverage_through_date = through_date,
        is_amendment=f1.is_amendment,
        amends_filing=amended_filing,
        amendment_number = f1.headers['report_number'] or None,
        header_data=header_line,
        filing_time=filing_time,
        filing_time_is_exact=filing_time_is_exact)
    
    this_filing_header.save(force_insert=True)

    
    """ Don't do this here--the new data--which is superceding the old data--is only queued for entry at this point
    The new data isn't necessarily loaded yet, so don't knock the old data out. If the old data gets knocked out before
    the new is loaded we may get a wrong sum. 
    
    This is now performed in mark_superceded_body_rows.py 
    
    # if it's got sked E's and it's an F3X, overwrite 24-hr reports
    if this_filing_header.form=='F3X':
            mark_superceded_F24s(this_filing_header)


    # if it's a F3 remove F65's        
    if this_filing_header.form=='F3':        
        mark_superceded_F65s(this_filing_header)
    """


    return True

