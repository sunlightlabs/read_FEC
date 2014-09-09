# check a state to see if candidate statuses have been set after a primary. Warns about too many candidates remaining in a race. 


from optparse import make_option

from summary_data.models import District, Candidate_Overlay

from summary_data.data_references import STATES_FIPS_DICT

from django.core.management.base import BaseCommand, CommandError



def comment_print(message):
    print "###  " + message + "\n"
    

def process_state(state):
    print "Checking primary for state='%s'" % (state)
    candidates = None
    
    if state in ['CA', 'LA', 'WA']:
        comment_print("Dealing with state %s" % (state))

        races = District.objects.filter(state=state, election_year=2014)

        for race in races:
            #print "Handling race %s" % (race)
    
            candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True).exclude(candidate_status__in=['W', 'LP', 'SP', 'SR', 'SG', 'SX', 'PR', 'LC']).order_by('-cash_on_hand')
            

            # There are two berths, so its competitive only if there are three spots
            if len(candidates) > 2:
                comment_print("Too many candidates remaining in jungle primary: %s %s %s" % (state, race.office, race.office_district))
                for candidate in candidates:
                    print "\t%s %s %s %s %s %s" % (candidate.name, candidate.fec_id, candidate.office, candidate.office_district, candidate.party, candidate.candidate_status)


    else:
        
        races = District.objects.filter(election_year=2014, state=state)

        
        for race in races:
            #print "Handling race %s" % (race)
            
            for party in ['D', 'R']:
                candidates = Candidate_Overlay.objects.filter(district=race, party=party).exclude(not_seeking_reelection=True).exclude(candidate_status__in=['W', 'LP', 'SP', 'SR', 'SG', 'SX', 'PR', 'LC']).order_by('-cash_on_hand')
                if len(candidates) > 1:
                    print "Too many candidates still in race after %s primary: %s %s %s" % (party, state, race.office, race.office_district)    
                    for candidate in candidates:
                        print "\t%s %s %s %s %s %s" % (candidate.name, candidate.fec_id, candidate.office, candidate.office_district, candidate.party, candidate.candidate_status)
    
    

class Command(BaseCommand):
    requires_model_validation = False
    
    

    
    def handle(self, *args, **options):
        for state in STATES_FIPS_DICT:
            # ignore states with primaries on Sept. 9
            if state in ['DE', 'MA', 'NH', 'LA', 'RI']:
                continue
            # ignore state with primary Nov. 4
            if state == 'LA':
                continue
            
            process_state(state)
        
