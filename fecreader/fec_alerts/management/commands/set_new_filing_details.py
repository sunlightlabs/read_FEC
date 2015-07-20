from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from fec_alerts.models import new_filing
from summary_data.utils.party_reference import get_party_from_pty
from ftpdata.models import Committee
from summary_data.models import Committee_Overlay
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing active cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'


def dateparse_notnull(datestring):
    """ dateparse returns today if given an empty string. Don't do that. """
    if datestring:
        datestring = datestring.strip()
        return dateparse(datestring)
    else:
        return None
        
# have standardized F3, F3X, F3P in sourcesalt directory.
def process_f3x_header(header_data):
    return_dict = {}
    return_dict['coh_end'] = header_data.get('col_a_cash_on_hand_close_of_period')
    return_dict['tot_raised'] = header_data.get('col_a_total_receipts')
    return_dict['tot_spent'] = header_data.get('col_a_total_disbursements')
    return_dict['new_loans'] = header_data.get('col_a_total_loans')
    return_dict['tot_ies'] = header_data.get('col_a_independent_expenditures')
    return_dict['tot_coordinated'] = header_data.get('col_a_coordinated_expenditures_by_party_committees')
    
    return return_dict
    
 
def process_f3_header(header_data):
    return_dict = {}
    return_dict['coh_end'] = header_data.get('col_a_cash_on_hand_close_of_period')
    return_dict['tot_raised'] = header_data.get('col_a_total_receipts')
    return_dict['tot_spent'] = header_data.get('col_a_total_disbursements')
    return_dict['new_loans'] = header_data.get('col_a_total_loans')
    
    
    return return_dict
    
def process_f5_header(header_data):
    return_dict= {}
    return_dict['tot_raised'] = header_data.get('total_contribution')
    return_dict['tot_spent'] = header_data.get('total_independent_expenditure')  

    # sometimes the dates are missing--in this case make sure it's set to None--this will otherwise default to today.
    return_dict['coverage_from_date'] = dateparse_notnull(header_data.get('coverage_from_date'))
    return_dict['coverage_to_date'] =dateparse_notnull(header_data.get('coverage_through_date'))   
        
    return return_dict
    
def process_f7_header(header_data):
    return_dict= {}
    return_dict['tot_spent'] = header_data.get('total_costs')    
    return_dict['coverage_from_date'] = dateparse_notnull(header_data.get('coverage_from_date'))
    return_dict['coverage_to_date'] =dateparse_notnull(header_data.get('coverage_through_date'))
    return return_dict

def process_f9_header(header_data):
    return_dict= {}
    return_dict['tot_raised'] = header_data.get('total_donations')
    return_dict['tot_spent'] = header_data.get('total_disbursements')    
    return_dict['coverage_from_date'] = dateparse_notnull(header_data.get('coverage_from_date'))
    return_dict['coverage_to_date'] =dateparse_notnull(header_data.get('coverage_through_date'))
    return return_dict
    

def process_f13_header(header_data):
    return_dict= {}
    return_dict['tot_raised'] = header_data.get('net_donations')
    return_dict['coverage_from_date'] = dateparse_notnull(header_data.get('coverage_from_date'))
    return_dict['coverage_to_date'] =dateparse_notnull(header_data.get('coverage_through_date'))
    return return_dict    
    
    net_donations
    

def handle_filing(this_filing):
    
    try:
        co = Committee_Overlay.objects.get(fec_id=this_filing.fec_id, cycle=this_filing.cycle)
        this_filing.committee_designation = co.designation
        this_filing.committee_name = co.name
        this_filing.committee_type = co.ctype
        this_filing.committee_slug = co.slug
        this_filing.party = co.party
        
        # mark that the committee is dirty
        co.is_dirty=True
        co.save()
        
    except Committee_Overlay.DoesNotExist:
        try:
            ## remember that ftpdata committees have cycles as ints, not strings. Not ideal. 
            if not this_filing.cycle:
                this_filing.cycle = CURRENT_CYCLE
            co = Committee.objects.get(cmte_id=this_filing.fec_id, cycle=int(this_filing.cycle))
            this_filing.committee_designation = co.cmte_dsgn
            this_filing.committee_type = co.cmte_tp
            this_filing.committee_name = co.cmte_name
            this_filing.party = get_party_from_pty(co.cmte_pty_affiliation)
        except Committee.DoesNotExist:
            pass
            
    
    header_data = this_filing.header_data
    
    form_type = this_filing.form_type
    parsed_data = {'coh_start':None, 'coh_end':None, 'new_loans':None,'tot_raised':None,'tot_spent':None}
    
    if form_type in ['F3A', 'F3N', 'F3T','F3PA', 'F3PN', 'F3PT', 'F3', 'F3P']:
        parsed_data = process_f3_header(header_data)
        print "got data %s" % (parsed_data)
        
        this_filing.coh_end =  parsed_data['coh_end'] if parsed_data['coh_end'] else 0
        this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else 0
        this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        this_filing.new_loans = parsed_data['new_loans'] if parsed_data['new_loans'] else 0
        this_filing.new_filing_details_set = True
        
    elif form_type in ['F3X', 'F3XA', 'F3XN', 'F3XT']:
        parsed_data = process_f3x_header(header_data)
        print "got data %s" % (parsed_data)
        
        this_filing.coh_end =  parsed_data['coh_end'] if parsed_data['coh_end'] else 0
        this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else 0
        this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        this_filing.new_loans = parsed_data['new_loans'] if parsed_data['new_loans'] else 0
        this_filing.tot_coordinated = parsed_data['tot_coordinated'] if parsed_data['tot_coordinated'] else 0
        this_filing.tot_ies = parsed_data['tot_ies'] if parsed_data['tot_ies'] else 0
        this_filing.new_filing_details_set = True
    
    
    elif form_type in ['F5', 'F5A', 'F5N']:
        parsed_data = process_f5_header(header_data)
        
        this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else 0
        this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        # total spending is total ies
        this_filing.tot_ies = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        this_filing.coverage_from_date = parsed_data['coverage_from_date']
        this_filing.coverage_to_date = parsed_data['coverage_to_date']
        
        try:
            this_filing.is_f5_quarterly = header_data['report_code'] in ['Q1', 'Q2', 'Q3', 'Q4', 'YE']
        except KeyError:
            # this is probably a problem. 
            pass
        this_filing.new_filing_details_set = True
        
        
    
    elif form_type in ['F7', 'F7A', 'F7N']:
        parsed_data = process_f7_header(header_data)
        #print "got data %s" % (parsed_data)
        this_filing.tot_raised = 0
        this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        this_filing.coverage_from_date = parsed_data['coverage_from_date'] if parsed_data['coverage_from_date'] else None
        this_filing.coverage_to_date = parsed_data['coverage_to_date'] if parsed_data['coverage_to_date'] else None
        this_filing.new_filing_details_set = True
        

    elif form_type in ['F9', 'F9A', 'F9N']:
        parsed_data = process_f9_header(header_data)
        
        this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else 0
        this_filing.tot_spent = parsed_data['tot_spent'] if parsed_data['tot_spent'] else 0
        this_filing.coverage_from_date = parsed_data['coverage_from_date'] if parsed_data['coverage_from_date'] else None
        this_filing.coverage_to_date = parsed_data['coverage_to_date'] if parsed_data['coverage_to_date'] else None
        this_filing.new_filing_details_set = True
        
    
    elif form_type in ['F13', 'F13A', 'F13N']:
        parsed_data = process_f13_header(header_data)
        #print "got data %s" % (parsed_data)
        
        this_filing.tot_raised = parsed_data['tot_raised'] if parsed_data['tot_raised'] else 0
        this_filing.coverage_from_date = parsed_data['coverage_from_date'] if parsed_data['coverage_from_date'] else None
        this_filing.coverage_to_date = parsed_data['coverage_to_date'] if parsed_data['coverage_to_date'] else None
        this_filing.new_filing_details_set = True
        
    else:
        # Nothing to be done, but mark this step as done. 
        this_filing.new_filing_details_set = True
        
    
    this_filing.save() 
    
    

class Command(BaseCommand):
    help = "Set data fields in the new filing from the parsed Filing_Header"
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        #new_filings_to_process = new_filing.objects.filter(previous_amendments_processed=False,header_is_processed=True).order_by('filing_number')        
        new_filings_to_process = new_filing.objects.filter(new_filing_details_set=False,header_is_processed=True).order_by('filing_number')        
        
        
        for this_filing in new_filings_to_process:
            print "processing %s " % (this_filing.filing_number)
            handle_filing(this_filing)
