import re
import os


from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId

from mongo.mongo_utils import get_db
from mongo.mongo_settings import FILING_HEADERS, FILING_LINES

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing

from parsing.read_FEC_settings import FILECACHE_DIRECTORY

# load up a form parser
fp = form_parser()

# get database, and collections
d = get_db()
headers = d[FILING_HEADERS]
lines = d[FILING_LINES]

unprocessable_form_hash = {}
parser_missing_hash = {}
verbose = True
test_threshold = 5000

def process_file(filingnum):
    #print "Processing filing %s" % (filingnum)
    f1 = filing(filingnum)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        if verbose:
            print "Not a parseable form: %s - %s" % (form, filingnum)
        try:
            count = unprocessable_form_hash[form]
            unprocessable_form_hash[form] = count + 1
        except KeyError:
            unprocessable_form_hash[form] = 1
            
        return

    if verbose:
        print "Found parseable form: %s - %s" % (form, filingnum)
    
    header = f1.get_first_row()
    print "header is %s" % header
    assert False
    body_rows =  f1.get_body_rows()
    #rows = f1.get_first_row()
    #print "rows: %s" % rows
    for row in body_rows:
        # the last line is empty, so don't try to parse it
        if len(row)>1:
            #if verbose:
            #    print "in filing: %s" % filingnum
            parsed_line = fp.parse_form_line(row, version)
            #if verbose:
            #    print parsed_line

def run_loop():
    filecount = 0
    for d, _, files in os.walk(FILECACHE_DIRECTORY):
        for a in files:

            filecount += 1
            filingnum = a.replace(".fec", "")

            if (filecount % 10000 == 0):
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

for i in (429146,):
    process_file(i)
#run_loop()
"""
print "Summary of unprocessable forms: "
for i in unprocessable_form_hash:
    print i, unprocessable_form_hash[i]
    
print "Summary of missing parsers: "
for i in parser_missing_hash:
    print i, parser_missing_hash[i]
"""