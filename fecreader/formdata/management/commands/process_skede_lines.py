from django.core.management.base import BaseCommand, CommandError
from datetime import date
from fec_alerts.models import new_filing
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay

cycle_start = date(2013,1,1)

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

def attach_ie_target(skedeline):
    candidate_id = skedeline.candidate_id_number    
    
    # If there's a candidate id, enter the data from the overlay
    if skedeline.expenditure_date_formatted >= cycle_start:
        
        if candidate_id:
        
        
            try: 
                this_candidate = Candidate_Overlay.objects.get(fec_id=candidate_id, cycle=('2014'))
                skedeline.candidate_id_checked = this_candidate.candidate_id_number
                skedeline.candidate_checked  = this_candidate
                skedeline.candidate_district_checked = this_candidate.office_district
                skedeline.candidate_district = this_candidate.district
                skedeline.candidate_office_checked = this_candidate.office
                skedeline.candidate_party_checked = this_candidate.party
                skedeline.candidate_state_checked = this_candidate.state
                skedeline.candidate_name_checked = this_candidate.name
                
                skedeline.support_oppose_checked = skedeline.support_oppose_code
                
                skedeline.save()
            
                return 1
        
            except Candidate_Overlay.DoesNotExist:
                print "Missing overlay for %s %s %s == %s" % (skedeline.candidate_last_name, skedeline.candidate_first_name, skedeline.expenditure_date_formatted, candidate_id)
                pass
        else:
            pass
            #print "Missing candidate id %s %s %s" % (skedeline.candidate_last_name, skedeline.candidate_first_name, skedeline.expenditure_date_formatted)
    
    else:
        # outta cycle expenditure
        pass
    
    ## TODO -- LOOKUP VIA RECONCILIATION TYPE ROUTINES HERE AND ONLY FALLBACK IF IT'S NOT FOUND THEN. 
    
    # fall back on data that's already there. 
    set_data_from_self(skedeline)
    return 0


    


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
                print "processing %s " % (this_filing.filing_number)
                print lines_present, lines_present['E']
                
                skedelines = SkedE.objects.filter(filing_number=this_filing.filing_number)
                
                for skede in skedelines:
                    attach_ie_target(skede)
            # mark that we've been processed. 
            this_filing.ie_rows_processed=True
            this_filing.save()