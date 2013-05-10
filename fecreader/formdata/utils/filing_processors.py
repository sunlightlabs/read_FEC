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
        
def mark_superceded_F24s(new_f3x_filing_header):
    print "marking superceded F24 body rows"
    
    # we only mark the child rows as superceded--the filing itself isn't, because it's possible, in theory, that it's *half* superceded. 
    coverage_from_date = new_f3x_filing_header.coverage_from_date
    coverage_through_date = new_f3x_filing_header.coverage_through_date
    raw_filer_id = new_f3x_filing_header.raw_filer_id
    
    SkedE.objects.filter(form_type__istartswith='F24', filer_committee_id_number=raw_filer_id, superceded_by_amendment=False, expenditure_date_formatted__gte=coverage_from_date, expenditure_date_formatted__lte=coverage_from_date).update(superceded_by_amendment=True)
    
        
def mark_superceded_F65s(new_f3_filing_header):
    print "marking superceded F65s"
    
    coverage_from_date = new_f3_filing_header.coverage_from_date
    coverage_through_date = new_f3_filing_header.coverage_through_date
    raw_filer_id = new_f3_filing_header.raw_filer_id
    
    SkedA.objects.filter(form_type__istartswith='F56', filer_committee_id_number=raw_filer_id, superceded_by_amendment=False, contribution_date__gte=coverage_from_date, contribution_date__lte=coverage_from_date).update(superceded_by_amendment=True)
    



def process_filing_header(filingnum, fp=None, filing_time=None, filing_time_is_exact=False):
    """ Enter the file header if needed. Post processing is still needed once it's complete. """
    
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


        
    Committee_Changed.objects.get_or_create(committee_id=f1.headers['fec_id'])
    
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
    return True

def post_process_filing(filing_number, linedict):
    
    this_filing_header = Filing_Header.objects.get(filing_number=filingnum)
    
    this_filing_header.lines_present = line_dict
    this_filing_header.entry_complete = True
    this_filing_header.save()


    # if this is an amended file, mark that the originals were superceded.
    if amended_filing:
        mark_superceded_amendment_header_rows(this_filing_header)

    # if it's got sked E's and it's an F3X, overwrite 24-hr reports
    if this_filing_header.form=='F3X':
        try:
            this_filing_header.lines_present['SchE']
            mark_superceded_F24s(this_filing_header)
        except KeyError:
            pass


    # if it's a F3 remove F65's        
    if this_filing_header.form=='F3':
        try:
            this_filing_header.lines_present['SchA']
            mark_superceded_F65s(this_filing_header)
        except KeyError:
            pass

    # NOT YET SURE: if it's a quarterly F5 ignore it, we think, maybe
    
        