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
    
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number WHERE fec_alerts_new_filing.filing_number = %s and superceded_by_amendment=False) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, filing_number, destination_file)
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
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number WHERE superceded_by_amendment=False and %s >= %s and is_superceded=False and fec_alerts_new_filing.fec_id = '%s') to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, datefield, CYCLE_START_STRING, committee_number, destination_file)
    cursor.execute(dumpcmd);

def dump_candidate_sked(sked_name, candidate_id, destination_file):
    """
    Blindly dump a csv file of a candidate's authorized committees, regardless of size. *Some filings are 200MB plus -- see #876048 or ACTBLUE's monthly stuff. 

    The rule is a body line is superceded EITHER if it's parent filing is superceded, or if the line itself is superceded. F24's and F6's are superceded line by line--though perhaps that could be improved on. 

    """

    # break if we're given junk args. 
    sked_name = sked_name.lower()
    assert sked_name in ['a', 'b']
    fieldlist = fields[sked_name]
    datefieldkey = "%s_date" % (sked_name)
    datefield = fields[datefieldkey]

    connection = get_connection()
    cursor = connection.cursor()
    
    ## first get the list of authorized committees. 
    acc_query = "select committee_id from  summary_data_authorized_candidate_committees where candidate_id='%s'" % candidate_id
    cursor.execute(acc_query);
    results = cursor.fetchall()
    committees = ["'" + x[0] + "'" for x in results]
    committee_formatted_list = ", ".join(committees)
    
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number WHERE superceded_by_amendment=False and %s >= %s and is_superceded=False and fec_alerts_new_filing.fec_id in (%s)) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, datefield, CYCLE_START_STRING, committee_formatted_list, destination_file)
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
    
    # need to join to get the committee name. 
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number  WHERE superceded_by_amendment=False and %s >= %s and is_superceded=False) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, datefield, CYCLE_START_STRING, destination_file)
    start = time.time()
    result = cursor.execute(dumpcmd);
    elapsed_time = time.time() - start
    print dumpcmd
    print "elapsed time for dumping sked %s: %s" % (sked_name, elapsed_time)
    
def dump_big_contribs(destination_file):
    # This is contributions to super-pacs greater than $5,000 + reported contributions to non-committees greater than $5,000, plus line 17 (other federal receipts) of $5,000 or more to hybrid pacs (see http://www.fec.gov/press/Press2011/20111006postcarey.shtml). Valid 'other federal receipts' incurred by the hybrid pac of $5,000 plus will also show up in this line... 
    
    ## update: The postcarey guidance is ignored on reports like this:
    ## http://docquery.fec.gov/cgi-bin/dcdev/forms/C00542217/882740/sa/11AI
    ## so instead just look at all lines there too....
    
    sked_name = 'a'
    fieldlist = fields[sked_name]
    datefieldkey = "%s_date" % (sked_name)
    datefield = fields[datefieldkey]

    connection = get_connection()
    cursor = connection.cursor()

    # need to join to get the committee name. 
    
    
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number  WHERE (memo_code isnull or not memo_code = 'X') and committee_type in ('I', 'O', 'U', 'V', 'W') and superceded_by_amendment=False and contribution_amount >= 10000 and %s >= %s and is_superceded=False) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, datefield, CYCLE_START_STRING, destination_file)
    #print dumpcmd
    start = time.time()
    result = cursor.execute(dumpcmd);
    elapsed_time = time.time() - start
    print "elapsed time for dumping big contribs: %s" % ( elapsed_time)
    
def dump_big_non_indiv_contribs(destination_file):
    # This is contributions to super-pacs greater than $5,000 + reported contributions to non-committees greater than $5,000, plus line 17 (other federal receipts) of $5,000 or more to hybrid pacs (see http://www.fec.gov/press/Press2011/20111006postcarey.shtml). Valid 'other federal receipts' incurred by the hybrid pac of $5,000 plus will also show up in this line... 

    sked_name = 'a'
    fieldlist = fields[sked_name]
    datefieldkey = "%s_date" % (sked_name)
    datefield = fields[datefieldkey]

    connection = get_connection()
    cursor = connection.cursor()

    # need to join to get the committee name. 
    dumpcmd = """copy (SELECT %s FROM formdata_sked%s left join fec_alerts_new_filing on formdata_sked%s.filing_number = fec_alerts_new_filing.filing_number  WHERE (memo_code isnull or not memo_code = 'X') and committee_type in ('I', 'O', 'U', 'V', 'W')  and contributor_organization_name <> '' and superceded_by_amendment=False and contribution_amount >= 10000 and %s >= %s and is_superceded=False) to '%s' with csv header quote as '"' escape as '\\'""" % (fieldlist, sked_name, sked_name, datefield, CYCLE_START_STRING, destination_file)
    #print dumpcmd
    start = time.time()
    result = cursor.execute(dumpcmd);
    elapsed_time = time.time() - start
    print "elapsed time for dumping big non-individual contribs: %s" % ( elapsed_time)