# hack to fix a bug that made celery-delegated processes bail on sked e's

import sys, time, os

sys.path.append('../../')


from parsing.filing import filing
from parsing.form_parser import form_parser, ParserMissingError
from fec_alerts.utils.form_mappers import *

from write_csv_to_db import CSV_dumper

from fec_import_logging import fec_logger
from hstore_helpers import dict_to_hstore

from db_utils import get_connection
verbose = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fecreader.settings")
from django.conf import settings
from fec_alerts.models import new_filing
from formdata.models import SkedE

class FilingHeaderDoesNotExist(Exception):
    pass
    
class FilingHeaderAlreadyProcessed(Exception):
    pass


def process_body_row(linedict, filingnum, header_id, is_amended, cd, filer_id):
    form = linedict['form_parser']
    
    ## Mark memo-ized rows as being superceded by an amendment.
    try:
        if linedict['memo_code']=='X':
            linedict['superceded_by_amendment'] = True
    except KeyError:
        pass
    
    #print "processing form type: %s" % (form)
    if form=='SchA':
        skeda_from_skedadict(linedict, filingnum, header_id, is_amended, cd)

    elif form=='SchB':
        skedb_from_skedbdict(linedict, filingnum, header_id, is_amended, cd)                        

    elif form=='SchE':
        skede_from_skededict(linedict, filingnum, header_id, is_amended, cd)

    # Treat 48-hour contribution notices like sked A.
    # Requires special handling for amendment, since these are superceded
    # by regular F3 forms. 
    elif form=='F65':
        skeda_from_f65(linedict, filingnum, header_id, is_amended, cd)

    # disclosed donor to non-commmittee. Sorta rare, but.. 
    elif form=='F56':
        skeda_from_f56(linedict, filingnum, header_id, is_amended, cd)

    # disclosed electioneering donor
    elif form=='F92':
        skeda_from_f92(linedict, filingnum, header_id, is_amended, cd)   

    # inaugural donors
    elif form=='F132':
        skeda_from_f132(linedict, filingnum, header_id, is_amended, cd)                    

    #inaugural refunds
    elif form=='F133':
        skeda_from_f133(linedict, filingnum, header_id, is_amended, cd)                    

    # IE's disclosed by non-committees. Note that they use this for * both * quarterly and 24- hour notices. There's not much consistency with this--be careful with superceding stuff. 
    elif form=='F57':
        skede_from_f57(linedict, filingnum, header_id, is_amended, cd)

    # Its another kind of line. Just dump it in Other lines.
    else:
        otherline_from_line(linedict, filingnum, header_id, is_amended, cd, filer_id)



def process_filing_body(filingnum, fp=None, logger=None):
    
    
    #It's useful to pass the form parser in when running in bulk so we don't have to keep creating new ones. 
    if not fp:
      fp = form_parser()
      
    if not logger:
        logger=fec_logger()
    msg = "process_filing_body: Starting # %s" % (filingnum)
    #print msg
    logger.info(msg)
      
    connection = get_connection()
    cursor = connection.cursor()
    cmd = "select fec_id, is_superceded, data_is_processed from fec_alerts_new_filing where filing_number=%s" % (filingnum)
    cursor.execute(cmd)
    
    cd = CSV_dumper(connection)
    
    result = cursor.fetchone()
    if not result:
        msg = 'process_filing_body: Couldn\'t find a new_filing for filing %s' % (filingnum)
        logger.error(msg)
        raise FilingHeaderDoesNotExist(msg)
        
    # will throw a TypeError if it's missing.
    header_id = 1
    is_amended = result[1]
    is_already_processed = result[2]
    if is_already_processed:
        msg = 'process_filing_body: This filing has already been entered.'
        logger.error(msg)
        raise FilingHeaderAlreadyProcessed(msg)
    
    #print "Processing filing %s" % (filingnum)
    try:
        f1 = filing(filingnum)
    except:
        print "*** couldn't handle filing %s" % (filingnum)
        return False
    form = f1.get_form_type()
    version = f1.get_version()
    filer_id = f1.get_filer_id()
    
    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        if verbose:
            msg = "process_filing_body: Not a parseable form: %s - %s" % (form, filingnum)
            # print msg
            logger.error(msg)
        return None
        
    linenum = 0
    while True:
        linenum += 1
        row = f1.get_body_row()
        if not row:
            break
        
        #print "row is %s" % (row)
        #print "\n\n\nForm is %s" % form
        try:
            linedict = fp.parse_form_line(row, version)
            if linedict['form_type'].upper().startswith('SE'):
                print "\n\n\nfiling %s form is %s transaction_id is: %s" % (filingnum, linedict['form_type'], linedict['transaction_id'])
                # make sure the transaction isn't already there before entering. 
                try:
                    SkedE.objects.get(filing_number=filingnum, transaction_id=linedict['transaction_id'])
                except SkedE.DoesNotExist:
                    process_body_row(linedict, filingnum, header_id, is_amended, cd, filer_id)

            elif linedict['form_type'].upper().startswith('SA'):
                print "\n\n\nfiling %s form is %s transaction_id is: %s" % (filingnum, linedict['form_type'], linedict['transaction_id'])
                # make sure the transaction isn't already there before entering. 
                try:
                    SkedA.objects.get(filing_number=filingnum, transaction_id=linedict['transaction_id'])
                    print "Already present! %s form is %s transaction_id is: %s" % (filingnum, linedict['form_type'], linedict['transaction_id'])
                except SkedA.DoesNotExist:
                    process_body_row(linedict, filingnum, header_id, is_amended, cd, filer_id)


            elif linedict['form_type'].upper().startswith('SB'):
                print "\n\n\nfiling %s form is %s transaction_id is: %s" % (filingnum, linedict['form_type'], linedict['transaction_id'])
                # make sure the transaction isn't already there before entering. 
                try:
                    SkedB.objects.get(filing_number=filingnum, transaction_id=linedict['transaction_id'])
                    print "Already present! %s form is %s transaction_id is: %s" % (filingnum, linedict['form_type'], linedict['transaction_id'])
                except SkedB.DoesNotExist:
                    process_body_row(linedict, filingnum, header_id, is_amended, cd, filer_id)
            
            
        except ParserMissingError:
            msg = 'process_filing_body: Unknown line type in filing %s line %s: type=%s Skipping.' % (filingnum, linenum, row[0])
            logger.warn(msg)
            continue
        except KeyError:
            "missing form type? in filing %s" % (filingnum)
    
    # commit all the leftovers
    cd.commit_all()
    cd.close()
    counter = cd.get_counter()
    total_rows = 0
    for i in counter:
        total_rows += counter[i]
        
    msg = "process_filing_body: Filing # %s Total rows: %s Tally is: %s" % (filingnum, total_rows, counter)
    # print msg
    logger.info(msg)
    
    
    # don't commit during testing of fix 
    
    # this data has been moved here. At some point we should pick a single location for this data. 
    header_data = dict_to_hstore(counter)
    cmd = "update fec_alerts_new_filing set lines_present='%s'::hstore where filing_number=%s" % (header_data, filingnum)
    cursor.execute(cmd)
    
    # mark file as having been entered. 
    cmd = "update fec_alerts_new_filing set data_is_processed = True where filing_number=%s" % (filingnum)
    cursor.execute(cmd)
    
    # flag this filer as one who has changed. 
    cmd = "update summary_data_committee_overlay set is_dirty=True where fec_id='%s'" % (filer_id)
    cursor.execute(cmd)
    
    #


if __name__ == '__main__':
    #filings = new_filing.objects.filter(filing_number__gt=1007393, data_is_processed=False, filing_is_downloaded=True, header_is_processed=True)
    
    fp = form_parser()
    
    filings = [1010304,]
    for this_filing in filings:

        process_filing_body(this_filing, fp=fp)


"""
t0 = time.time()
process_filing_body(864353)
# 869853, 869866
#for fn in [869888]:
#    process_filing_body(fn, fp)
t1 = time.time()
print "total time = " + str(t1-t0)
# long one: 767168
#FAILS WITH STATE ADDRESS PROBLEM:  biggest one on file: 838168 (510 mb) - act blue - 2012-10-18         | 2012-11-26
# second biggest: 824988 (217.3mb) - act blue - 2012-10-01         | 2012-10-17 - 874K lines
# 840327 - 169MB  C00431445 - OFA   | 2012-10-18         | 2012-11-26
# 821325 - 144 mb Obama for america 2012-09-01         | 2012-09-30
# 798883 - 141 mb
# 804867 - 127 mb
# 827978 - 119 mb
# 754317 - 118 mb

"""


