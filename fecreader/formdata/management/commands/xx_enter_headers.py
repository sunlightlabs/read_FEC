""" deprecated now """


import os

from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.models import Filing_Header

# load up a form parser
fp = form_parser()

unprocessable_form_hash = {}
parser_missing_hash = {}
verbose = True
test_threshold = 1000000

def process_file(filingnum):
    #print "Processing filing %s" % (filingnum)
    f1 = filing(filingnum, read_from_cache=True, write_to_cache=True)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        #if verbose:
        #    print "Not a parseable form: %s - %s" % (form, filingnum)
        try:
            count = unprocessable_form_hash[form]
            unprocessable_form_hash[form] = count + 1
        except KeyError:
            unprocessable_form_hash[form] = 1
            
        return

    #if verbose:
    #    print "Found parseable form: %s - %s" % (form, filingnum)
    
    header = f1.get_first_row()
    header_line = fp.parse_form_line(header, version)

    amended_filing=None
    if f1.is_amendment:
        amended_filing = f1.headers['filing_amended']

    # enter it if we don't have it already:
    try:    
        already_entered = Filing_Header.objects.get(filing_number=filingnum)
        print "Already entered! %s" % (filingnum)
        return 0
        
    except Filing_Header.DoesNotExist:
        
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
        
        new_header_id = Filing_Header.objects.create(
            raw_filer_id=f1.headers['fec_id'],
            form=form,
            filing_number=filingnum,
            version=f1.version,
            coverage_from_date=from_date,
            coverage_through_date = through_date,
            is_amendment=f1.is_amendment,
            amends_filing=amended_filing,
            amendment_number = f1.headers['report_number'] or None,
            header_data=header_line)
            
            
        #print "Added header with id %s" % new_header_id

    
        """
        body_rows =  f1.get_body_rows()
        for row in body_rows:
            # the last line is empty, so don't try to parse it
            if len(row)>1:
                # Don't double check, just enter the data. 
                parsed_line = fp.parse_form_line(row, version)
                parsed_line['filing_number'] = int(filingnum)
                #if verbose:
                #    print parsed_line
                new_line_id = filing_lines.insert(parsed_line)
        """
    
        return 1
    

def run_loop():
    filecount = 0
    filemin = 0
    for d, _, files in os.walk(FILECACHE_DIRECTORY):
        for a in files:

            filingnum = a.replace(".fec", "")
            if int(filingnum) < filemin:
                continue
                
            filecount += 1
            
            if (filecount % 1000 == 0):
                print "Processed %s lines" % (filecount)

            if filecount > test_threshold:
                break

            try:
                process_file(filingnum)
            except ParserMissingError, e:
                print filingnum, e
                try: 
                    count = parser_missing_hash[e]
                    parser_missing_hash[e] = e + 1
                except KeyError:
                    parser_missing_hash[e] = 1
    print "Processed %s files" % filecount    


class Command(BaseCommand):
    help = "Enter file headers; don't mark them as either amended or not."
    requires_model_validation = False

    def handle(self, *args, **options):
        #for i in (711848,):
        #    process_file(i)
        run_loop()
   