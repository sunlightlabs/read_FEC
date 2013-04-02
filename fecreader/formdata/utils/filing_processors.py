from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.models import Filing_Header

from formdata.utils.form_mappers import *

verbose = True




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
    

def process_body_row(form, linedict, filingnum, header):
    #print "processing header row with header amendment %s" % (header.is_superceded)
    if form=='SchA':
        skeda_from_skedadict(linedict, filingnum, header)
        
    elif form=='SchB':
        skedb_from_skedbdict(linedict, filingnum, header)                        
        
    elif form=='SchE':
        skede_from_skededict(linedict, filingnum, header)
    
    # Treat 48-hour contribution notices like sked A.
    # Requires special handling for amendment, since these are superceded
    # by regular F3 forms. 
    elif form=='F65':
        skeda_from_f65(linedict, filingnum, header)
        
    # disclosed donor to non-commmittee. Sorta rare, but.. 
    elif form=='F56':
        skeda_from_f56(linedict, filingnum, header)
    
    # disclosed electioneering donor
    elif form=='F92':
        skeda_from_f92(linedict, filingnum, header)   
    
    # inaugural donors
    elif form=='F132':
        skeda_from_f132(linedict, filingnum, header)                    
    
    #inaugural refunds
    elif form=='F133':
        skeda_from_f133(linedict, filingnum, header)                    
    
    # IE's disclosed by non-committees. Note that they use this for * both * quarterly and 24- hour notices. There's not much consistency with this--be careful with superceding stuff. 
    elif form=='F57':
        skede_from_f57(linedict, filingnum, header)

    # Its another kind of line. Just dump it in Other lines.
    else:
        otherline_from_line(linedict, filingnum, header, formname=form)


def process_file(filingnum, fp=None, filing_time=None, filing_time_is_exact=False):
    
    if not fp:
        fp = form_parser()
        
    #print "Processing filing %s" % (filingnum)
    f1 = filing(filingnum, read_from_cache=True, write_to_cache=True)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        if verbose:
            print "Not a parseable form: %s - %s" % (form, filingnum)

            
        return

    header = f1.get_first_row()
    header_line = fp.parse_form_line(header, version)

    amended_filing=None
    if f1.is_amendment:
        amended_filing = f1.headers['filing_amended']

    header_needs_entry = True
    rows_need_entry = True
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
    
    if not header_needs_entry and not rows_need_entry:
        #We're done. Probably the previous amendments have been set -- if not and we're here for some other reason, the amendments should be fixed in a daily-ish cleanup.
        print "Filing totally entered"
        return None
        
    if header_needs_entry or rows_need_entry:
        # mark that we're about to mess with this committee id.
        Committee_Changed.objects.get_or_create(committee_id=f1.headers['fec_id'])
        
    if header_needs_entry:
        
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
       
    if rows_need_entry:
        # Now enter content rows:
        line_dict = {}
        content_rows = f1.get_body_rows()
        total_lines = 0
        for row in content_rows:
            # instead of parsing the line, just assume form type is the first arg.
            r_type = row[0].upper().strip()
        
            # sometimes there are blank lines within files--see 707076.fec
            if not r_type:
                continue
            
            total_lines += 1
            # what type of line parser would be used here? 
            lp = fp.get_line_parser(r_type)
            if lp:
                form = lp.form
                r_type = form
                #print "line parser: %s from %s" % (form, r_type)
            
                linedict = fp.parse_form_line(row, version)

                process_body_row(form, linedict, filingnum, this_filing_header)
            
            else:
                print "Missing parser from %s" % (r_type) 
        
            try: 
                num = line_dict[r_type]
                line_dict[r_type] = num + 1
            except KeyError:
                line_dict[r_type] = 1
        
        
    # We finished entering the line. Add the line mapping dict, and set the complete flag. 
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
    
    
            
            