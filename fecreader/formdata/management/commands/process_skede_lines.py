from django.core.management.base import BaseCommand, CommandError
from datetime import date
from fec_alerts.models import new_filing
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay
from reconciliation.fec_reconciler import match_by_name, run_fec_query

from add_committees_to_skede import attach_committee_to_skedeline

from shared_utils.cycle_utils import get_cycle_from_date


def set_data_from_self(skedeline):
    
    name = None
    if skedeline.candidate_middle_name:
        name = "%s, %s %s" % (skedeline.candidate_last_name, skedeline.candidate_first_name,  skedeline.candidate_middle_name)
    else:
        name = "%s, %s" % (skedeline.candidate_last_name, skedeline.candidate_first_name)
        
    skedeline.candidate_district_checked = skedeline.candidate_district
    skedeline.candidate_office_checked = skedeline.candidate_office
    skedeline.candidate_state_checked = skedeline.candidate_state
    skedeline.candidate_name_checked = name
    skedeline.support_oppose_checked = skedeline.support_oppose_code
    skedeline.save()


    
def set_data_from_candidate_id(skedeline, candidate_id):
    
    cycle_date = skedeline.effective_date
    THIS_CYCLE = None
    if cycle_date:
        THIS_CYCLE = get_cycle_from_date(cycle_date)
        
    try: 
        this_candidate = Candidate_Overlay.objects.get(fec_id=candidate_id, cycle=(THIS_CYCLE))
        skedeline.candidate_id_checked = this_candidate.fec_id
        skedeline.candidate_checked  = this_candidate
        skedeline.candidate_district_checked = this_candidate.office_district
        skedeline.district_checked = this_candidate.district
        skedeline.candidate_office_checked = this_candidate.office
        skedeline.candidate_party_checked = this_candidate.party
        skedeline.candidate_state_checked = this_candidate.state
        skedeline.candidate_name_checked = this_candidate.name
        skedeline.support_oppose_checked = skedeline.support_oppose_code
        skedeline.save()
        return True

    except Candidate_Overlay.DoesNotExist:
        print "Missing candidate overlay for %s filing %s" % (candidate_id, skedeline.filing_number)
        return False
        



def fuzzy_match_candidate(skedeline):
    state = skedeline.candidate_state
    name_to_check = "%s, %s" % (skedeline.candidate_last_name, skedeline.candidate_first_name)
    office = skedeline.candidate_office
    state = skedeline.candidate_state
    
    cycle_date = skedeline.effective_date
    THIS_CYCLE = None
    if cycle_date:
        THIS_CYCLE = get_cycle_from_date(cycle_date)
    
    result = run_fec_query(name_to_check, state=state, office=office, cycle=THIS_CYCLE, fuzzy=True)
    if result:
        if result[0]['match']:
            print "Fuzzy matching matched %s, %s, %s to %s with id %s" % (name_to_check, state, office, result[0]['name'], result[0]['id'])
        
            return set_data_from_candidate_id(skedeline, result[0]['id'])
    
    print "Fuzzy matching couldn't match %s, %s, %s" % (name_to_check, state, office)
    return False
    


def attach_ie_target(skedeline):
    candidate_id = skedeline.candidate_id_number   
    
    
    # If there's a candidate id, enter the data from the overlay
    if candidate_id:
        result = set_data_from_candidate_id(skedeline, candidate_id)
    
        if result:
            return True

    else:

        # if we're still here, try a fuzzy match

        fuzzy_match_result = fuzzy_match_candidate(skedeline)
        if fuzzy_match_result:
            return True

        # fall back on data that's already there. 
        set_data_from_self(skedeline)
        return False

    


class Command(BaseCommand):
    help = "Set the name and details of the candidate targetted"
    requires_model_validation = False
    

    def handle(self, *args, **options):
        filings_to_process = new_filing.objects.filter(data_is_processed=True, body_rows_superceded=True).exclude(ie_rows_processed=True).order_by('filing_number')
        for this_filing in filings_to_process:
            lines_present = this_filing.lines_present
            has_sked_E = False
            try:
                lines_present['E']
                if int(lines_present['E']) > 0:
                    has_sked_E = True
            except KeyError:
                continue
            
            if has_sked_E:
                #print "processing %s " % (this_filing.filing_number)
                #print lines_present, lines_present['E']
                
                skedelines = SkedE.objects.filter(filing_number=this_filing.filing_number)
                
                for skede in skedelines:
                    attach_committee_to_skedeline(skede)
                    attach_ie_target(skede)
            # mark that we've been processed. 
            this_filing.ie_rows_processed=True
            this_filing.save()