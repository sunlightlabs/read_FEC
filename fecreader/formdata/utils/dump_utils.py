import sys, time

from db_utils import get_connection
from dumper_field_reference import fields


CYCLE_START_STRING="date('20130101')"

def dump_filing_sked(sked_name, filing_number, destination_file):
    """
    Blindly dump a csv file of an entire filing, regardless of size. *Some filings are 200MB plus -- see #876048 or ACTBLUE's monthly stuff. 
    """
    
    # break if we're given junk args. 
    sked_name = sked_name.lower()
    assert sked_name in ['a', 'b', 'e']
    filing_number = int(filing_number)
    fieldlist = fields[sked_name]
    
    connection = get_connection()
    cursor = connection.cursor()
    
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s WHERE filing_number = %s and superceded_by_amendment=False) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, filing_number, destination_file)
    cursor.execute(dumpcmd);

def dump_committee_sked(sked_name, committee_number, destination_file):
    """
    Blindly dump a csv file of an entire committee, regardless of size. *Some filings are 200MB plus -- see #876048 or ACTBLUE's monthly stuff. 
    
    The rule is a body line is superceded EITHER if it's parent filing is superceded, or if the line itself is superceded. F24's and F6's are superceded line by line--though perhaps that could be improved on. 
    
    """
    
    # break if we're given junk args. 
    sked_name = sked_name.lower()
    assert sked_name in ['a', 'b', 'e']
    fieldlist = fields[sked_name]
    datefieldkey = "%s_date" % (sked_name)
    datefield = fields[datefieldkey]
    
    connection = get_connection()
    cursor = connection.cursor()
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s WHERE superceded_by_amendment=False and %s >= %s and filing_number in (select filing_number from fec_alerts_new_filing where fec_id='%s' and is_superceded=False)) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, datefield, CYCLE_START_STRING, committee_number, destination_file)
    cursor.execute(dumpcmd);

def dump_all_sked(sked_name, destination_file):
    

    # break if we're given junk args. 
    sked_name = sked_name.lower()
    assert sked_name in ['a', 'b', 'e']
    fieldlist = fields[sked_name]
    datefieldkey = "%s_date" % (sked_name)
    datefield = fields[datefieldkey]
    
    connection = get_connection()
    cursor = connection.cursor()
    
    # This might
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s WHERE superceded_by_amendment=False and %s >= %s and filing_number in (select filing_number from fec_alerts_new_filing where is_superceded=False)) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, datefield, CYCLE_START_STRING, destination_file)
    #dumpcmd = """copy (SELECT %s FROM formdata_sked%s WHERE superceded_by_amendment=False and %s >= %s) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, datefield, CYCLE_START_STRING, destination_file)
    start = time.time()
    result = cursor.execute(dumpcmd);
    elapsed_time = time.time() - start
    print "elapsed time for dump: %s" % (elapsed_time)