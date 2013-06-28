from dateutil.parser import parse as dateparse

from hstore_helpers import dict_to_hstore

        
def validate_decimal(value):
    # not actually validating, just nullifying it if it's empty.
    
    # float('') = 0.0. WTF python? 
    if not value:
        return None
        
    else:
        try:
            return float(value)
        except ValueError:
            print "Error converting contribution amount %s" % (value)
            return None
            
            
def clean_form_type(formtype):
    return formtype.upper().strip()
    


## Form mappers follow below. Refactor once this is stable. Just trying to handle all the cases first. 
    
def skeda_from_skedadict(data_dict, filing_number, header_row_id, is_amended, cd):
    """ We can either pass the header row in or not; if not, look it up."""
    
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['header_id'] = header_row_id
    data_dict['superceded_by_amendment'] = is_amended        
    data_dict['filing_number'] = filing_number
    
    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    data_dict['contribution_aggregate'] = validate_decimal(data_dict['contribution_aggregate'])
    
    cd.writerow('A', data_dict)
    


def skeda_from_f65(data_dict, filing_number, header_row_id, is_amended, cd):
    """ Enter 48-hour contributions to candidate as if it were a sked A. Will later be superceded by periodic F3 report.This is almost to skeda_from_skedadict b/c I modified the F65.csv to match, but"""
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['header_id'] = header_row_id

    data_dict['superceded_by_amendment'] = is_amended
    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    # no contribution aggregates on F65s
    
    
    cd.writerow('A', data_dict)
    
# see 847857
def skeda_from_f56(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['header_id'] = header_row_id
    

    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    # no contribution aggregates on F65s
    cd.writerow('A', data_dict)
    
    
# skeda_from_f92 -- electioneering communication contribs

def skeda_from_f92(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['header_id'] = header_row_id
    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
        
    cd.writerow('A', data_dict)


# inaugural donors
def skeda_from_f132(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['header_id'] = header_row_id
    data_dict['filing_number'] = filing_number

    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass

    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])

    cd.writerow('A', data_dict)

# inaugural donor refunds. Make sure amounts are ! negative
def skeda_from_f133(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['header_id'] = header_row_id
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['filing_number'] = filing_number
    
    # map refund to contributions
    data_dict['contribution_amount'] = data_dict['refund_amount']
    data_dict['contribution_date'] = data_dict['refund_date']    
    
    # so logging doesn't complain about unexpected value
    del data_dict['refund_date']
    del data_dict['refund_amount']
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    
    # flip signs if this is positive. 
    if data_dict['contribution_amount']  > 0:
        data_dict['contribution_amount'] = 0-data_dict['contribution_amount']

    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass

    cd.writerow('A', data_dict)
    

def skedb_from_skedbdict(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['header_id'] = header_row_id
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['filing_number'] = filing_number
    
    # This key is too long. Use shortened version. 
    data_dict['ref_to_sys_code_ids_acct'] = data_dict['reference_to_si_or_sl_system_code_that_identifies_the_account']
    del data_dict['reference_to_si_or_sl_system_code_that_identifies_the_account']

    if data_dict['expenditure_date']:
        try:
            data_dict['expenditure_date_formatted'] = dateparse(data_dict['expenditure_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass

    data_dict['expenditure_amount'] = validate_decimal(data_dict['expenditure_amount'])
    data_dict['semi_annual_refunded_bundled_amt'] = validate_decimal(data_dict['semi_annual_refunded_bundled_amt'])

    cd.writerow('B', data_dict)
    
    
def skede_from_skededict(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['header_id'] = header_row_id
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['filing_number'] = filing_number

    if data_dict['expenditure_date']:
        try:
            data_dict['expenditure_date_formatted'] = dateparse(data_dict['expenditure_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass


    data_dict['expenditure_amount'] = validate_decimal(data_dict['expenditure_amount'])
    data_dict['calendar_y_t_d_per_election_office'] = validate_decimal(data_dict['calendar_y_t_d_per_election_office'])

    #model_instance = SkedE()
    
    cd.writerow('E', data_dict)
    
    
def skede_from_f57(data_dict, filing_number, header_row_id, is_amended, cd):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['header_id'] = header_row_id
    data_dict['filing_number'] = filing_number

    if data_dict['expenditure_date']:
        try:
            data_dict['expenditure_date_formatted'] = dateparse(data_dict['expenditure_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass


    data_dict['expenditure_amount'] = validate_decimal(data_dict['expenditure_amount'])
    data_dict['calendar_y_t_d_per_election_office'] = validate_decimal(data_dict['calendar_y_t_d_per_election_office'])

    cd.writerow('E', data_dict)
    

def otherline_from_line(data_dict, filing_number, header_row_id, is_amended, cd, filer_id):
    data_dict['transaction_id'] = data_dict['transaction_id'][:20]
    data_dict['superceded_by_amendment'] = is_amended
    data_dict['line_data'] = dict_to_hstore(data_dict)
    data_dict['header_id'] = header_row_id
    data_dict['filing_number'] = filing_number

    data_dict['filer_committee_id_number'] = filer_id
    
    
    # text records use rec_type instead of form. I dunno. 
    try: 
        data_dict['form_type'] = data_dict['rec_type']
    except KeyError:
        pass

    cd.writerow('O', data_dict)
    