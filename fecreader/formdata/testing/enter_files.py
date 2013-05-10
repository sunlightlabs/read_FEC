## crap to run this 
import sys, os

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/fecreader/')
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/')

import settings
setup_environ(settings)

##

import time

from parsing.form_parser import form_parser, ParserMissingError
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.utils.filing_processors import process_filing_header



def get_file_list(filemin=0, list_length=100):
    filecount = 0
    arraylist = []
    for d, _, files in os.walk(FILECACHE_DIRECTORY):
        for a in files:
            filingnum = a.replace(".fec", "")
            if int(filingnum) < filemin:
                continue
            filecount += 1
            if filecount > list_length:
                break
            arraylist.append(filingnum)
    return arraylist

#file_list = get_file_list(767159, 1000)
# some of the biggest files
file_list = [838168, 824988, 840327, 821325, 798883, 804867, 827978, 754317]
start_time = time.time()
print file_list

count = 0
for i in (file_list):
    count += 1
    print "Processing #%s : %s" % (count, i)
    process_filing_header(i)
    
elapsed_time = time.time() - start_time
print "Elapsed time = %s seconds" % (elapsed_time)

