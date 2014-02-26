# How many primaries will be hard-fought?

import sys, os

from django.core.management import setup_environ
sys.path.append('../fecreader/')
sys.path.append('../')

import settings
setup_environ(settings)

from django.template import Template
from django.template.loader import get_template
from django.template import Context

from summary_data.models import District, Candidate_Overlay

#house_fundraising_threshold = 100000
#senate_fundraising_threshold = 500000

#house_cash_on_hand_threshold = 30000
#senate_cash_on_hand_threshold = 50000

house_fundraising_threshold = 10000
senate_fundraising_threshold = 50000

house_cash_on_hand_threshold = 3000
senate_cash_on_hand_threshold = 5000

def comment_print(message):
    print "###  " + message + "\n"
    
########
# Deal with jungle primary states first: CA, WA, LA
########

competitive_races = {}
competitive_races['senate']=[]
competitive_races['house']=[]


comment_print("Dealing with jungle primary states")

for state in ['CA', 'LA', 'WA']:
    comment_print("Dealing with state %s" % (state))
    
    races = District.objects.filter(state=state, election_year=2014)
    
    for race in races:
        
        candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True)
        if race.office == 'H':
            candidates = candidates.filter(total_receipts__gte=house_fundraising_threshold,cash_on_hand__gte=house_cash_on_hand_threshold)
        else:
            candidates = candidates.filter(total_receipts__gte=senate_fundraising_threshold,cash_on_hand__gte=senate_cash_on_hand_threshold)
            

        # There are two berths, so its competitive only if there are three spots
        if len(candidates) > 2:
            comment_print("Multiple candidates found !")
            this_race_object = {}
            this_race_object['race'] = race
            this_race_object['candidates'] = []
            print "State=%s Office =%s District =%s incumbent=%s incumbent party = %s is open %s rating: %s (%s)" % (race.state, race.office, race.office_district, race.incumbent_name, race.incumbent_party, race.open_seat,  race.rothenberg_rating_text, race.rothenberg_rating_id)
            
            for candidate in candidates:
                print "\tcandidate: %s party: %s incumbent: %s total raised: %s cash on hand %s (as of %s)" % (candidate.name, candidate.party, candidate.is_incumbent, candidate.total_receipts, candidate.cash_on_hand, candidate.cash_on_hand_date )
                this_race_object['candidates'].append(candidate)
            print "\n\n"
            if race.office == 'H':
                competitive_races['house'].append(this_race_object)
            else:
                competitive_races['senate'].append(this_race_object)
                
            
    
## all other states

races = District.objects.filter(election_year=2014).exclude(state__in=['CA', 'WA', 'LA'])

for race in races:
    
    candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True)
    if race.office == 'H':
        candidates = candidates.filter(total_receipts__gte=house_fundraising_threshold,cash_on_hand__gte=house_cash_on_hand_threshold)
    else:
        candidates = candidates.filter(total_receipts__gte=senate_fundraising_threshold,cash_on_hand__gte=senate_cash_on_hand_threshold)
        
    for party in ['D', 'R']:
        party_candidates = candidates.filter(party=party)
        if len(party_candidates) > 1:
            this_race_object = {}
            this_race_object['race'] = race
            this_race_object['candidates'] = []
            
            print "State=%s Office =%s District =%s incumbent=%s incumbent party = %s is open %s rating: %s (%s)" % (race.state, race.office, race.office_district, race.incumbent_name, race.incumbent_party, race.open_seat,  race.rothenberg_rating_text, race.rothenberg_rating_id)
            
            for candidate in party_candidates:
                print "\tcandidate: %s party: %s incumbent: %s total raised: %s cash on hand %s (as of %s)" % (candidate.name, candidate.party, candidate.is_incumbent, candidate.total_receipts, candidate.cash_on_hand, candidate.cash_on_hand_date )
                this_race_object['candidates'].append(candidate)
                
            print "\n\n"
            if race.office == 'H':
                competitive_races['house'].append(this_race_object)
            else:
                competitive_races['senate'].append(this_race_object)            

print "primaries are: %s" % competitive_races

senate_races = sorted(competitive_races['senate'], key=lambda x: x['race'].state)
house_races = sorted(competitive_races['house'], key=lambda x: (x['race'].state, x['race'].office_district ))

c = Context({"house_races": house_races, "senate_races":senate_races})
this_template = get_template('generated_pages/primary_list.html')
result = this_template.render(c)
print result