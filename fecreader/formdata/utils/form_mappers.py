from dateutil.parser import parse as dateparse

from django.db import IntegrityError, transaction

from formdata.models import *

""" Some helpers to wrap parsed dicts to models.
"""


skedadict = {}
skedafields = SkedA._meta.get_all_field_names()
for field in skedafields:
    skedadict[field]=1
    
skedbdict = {}
skedbfields = SkedB._meta.get_all_field_names()
for field in skedbfields:
    skedbdict[field]=1

skededict = {}
skedefields = SkedE._meta.get_all_field_names()
for field in skedefields:
    skededict[field]=1
        
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
    


@transaction.commit_manually
def create_instance_from_dict(model_instance, data_dict, field_dict):
    """ Create a model instance by populating only the fields that are part of the model--ignore other keys. Commit manually, and catch a database integrity error; otherwise postgres will freak out """
    
    try:
        data_dict['form_type'] = clean_form_type(data_dict['form_type'])
    except KeyError:
        print "Missing form type"
    
    for key in data_dict:
        try:
            a = field_dict[key]
            setattr(model_instance, key, data_dict[key])
        except KeyError:
            print "Ignoring attribute %s" % key
    
    return None
    """
    newmodelid = None
    try:
        newmodelid = model_instance.save()
    except IntegrityError:
        print "Transaction failed!!"
        transaction.rollback()
    else:
        transaction.commit()
    
    return newmodelid
    """
   
    
## Form mappers follow below. Refactor once this is stable. Just trying to handle all the cases first. 
    
def skeda_from_skedadict(data_dict, filing_number, header_row=None):
    """ We can either pass the header row in or not; if not, look it up."""
    if not header_row:
        print "looking up sked header"
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row
        
    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number
    
    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    data_dict['contribution_aggregate'] = validate_decimal(data_dict['contribution_aggregate'])
    
    model_instance = SkedA()
    
    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id

def skeda_from_f65(data_dict, filing_number, header_row=None):
    """ Enter 48-hour contributions to candidate as if it were a sked A. Will later be superceded by periodic F3 report.This is almost to skeda_from_skedadict b/c I modified the F65.csv to match, but"""
    
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    # no contribution aggregates on F65s
    
    model_instance = SkedA()
    
    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id
    
# see 847857
def skeda_from_f56(data_dict, filing_number, header_row=None):
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    # no contribution aggregates on F65s
    
    model_instance = SkedA()
    
    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id
    
# skeda_from_f92 -- electioneering communication contribs

def skeda_from_f92(data_dict, filing_number, header_row=None):
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number


    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass
    
    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])
    
    model_instance = SkedA()
    
    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id


# inaugural donors
def skeda_from_f132(data_dict, filing_number, header_row=None):
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number

    if data_dict['contribution_date']:
        try:
            data_dict['contribution_date_formatted'] = dateparse(data_dict['contribution_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass

    data_dict['contribution_amount'] = validate_decimal(data_dict['contribution_amount'])

    model_instance = SkedA()

    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id

# inaugural donor refunds. Make sure amounts are ! negative
def skeda_from_f133(data_dict, filing_number, header_row=None):
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
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


    model_instance = SkedA()

    created_id = create_instance_from_dict(model_instance, data_dict, skedadict)
    return created_id

def skedb_from_skedbdict(data_dict, filing_number, header_row=None):
    """ We can either pass the header row in or not; if not, look it up."""
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
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

    model_instance = SkedB()

    created_id = create_instance_from_dict(model_instance, data_dict, skedbdict)
    return created_id
    
def skede_from_skededict(data_dict, filing_number, header_row=None):
    """ We can either pass the header row in or not; if not, look it up."""
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number

    if data_dict['expenditure_date']:
        try:
            data_dict['expenditure_date_formatted'] = dateparse(data_dict['expenditure_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass


    data_dict['expenditure_amount'] = validate_decimal(data_dict['expenditure_amount'])
    data_dict['calendar_y_t_d_per_election_office'] = validate_decimal(data_dict['calendar_y_t_d_per_election_office'])

    model_instance = SkedE()

    created_id = create_instance_from_dict(model_instance, data_dict, skededict)
    return created_id
    
def skede_from_f57(data_dict, filing_number, header_row=None):
    """ We can either pass the header row in or not; if not, look it up."""
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)
        data_dict['header'] = header_row

    data_dict['superceded_by_amendment'] = header_row.is_superceded
    data_dict['filing_number'] = filing_number

    if data_dict['expenditure_date']:
        try:
            data_dict['expenditure_date_formatted'] = dateparse(data_dict['expenditure_date'])
        except ValueError:
            # if we can't parse the date, just ignore it. 
            pass


    data_dict['expenditure_amount'] = validate_decimal(data_dict['expenditure_amount'])
    data_dict['calendar_y_t_d_per_election_office'] = validate_decimal(data_dict['calendar_y_t_d_per_election_office'])

    model_instance = SkedE()

    created_id = create_instance_from_dict(model_instance, data_dict, skededict)
    return created_id

@transaction.commit_manually
def otherline_from_line(data_dict, filing_number, header_row=None, formname=None):
    """ We can either pass the header row in or not; if not, look it up."""
    if not header_row:
        header_row =  Filing_Header.objects.get(filing_number=filing_number)

    superceded_by_amendment = header_row.is_superceded
    filer_committee_id_number = header_row.raw_filer_id
    
    transaction_id = None
    form_type = None
    
    # text records use rec_type instead of form. I dunno. 
    try: 
        data_dict['form_type'] = data_dict['rec_type']
    except KeyError:
        pass
    
    try:
        transaction_id = data_dict['transaction_id']
    except KeyError:
        pass

    try:
        form_type = data_dict['form_type']
    except KeyError:
        pass
    
    
    newmodelid = None
    try:
        newmodelid = OtherLine.objects.create(
            header=header_row,
            filing_number=filing_number,
            superceded_by_amendment=superceded_by_amendment,
            form_parser=formname,
            form_type=form_type,
            filer_committee_id_number=filer_committee_id_number,
            transaction_id=transaction_id,
            line_data=data_dict
        )
    except IntegrityError:
        print "Transaction failed!!"
        print "Filing %s committee %s formtype %s transaction_id %s" % (filing_number, filer_committee_id_number, form_type, transaction_id)
        print "\n%s" % (data_dict)
        transaction.rollback()
    else:
        transaction.commit()

    return newmodelid
        