# How many primaries will be hard-fought?

from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Q

from summary_data.models import District, Candidate_Overlay, Election

from django.core.management.base import BaseCommand, CommandError


house_fundraising_threshold = 100000
senate_fundraising_threshold = 300000

house_cash_on_hand_threshold = 50000
senate_cash_on_hand_threshold = 150000

today = date.today()

PROJECT_ROOT = settings.PROJECT_ROOT

def comment_print(message):
    print "###  " + message + "\n"
    
########
# Deal with jungle primary states first: CA, WA, LA
########


class Command(BaseCommand):
    help = "Regenerate the static competitive primary page."
    requires_model_validation = False
    
    
    def handle(self, *args, **options):

        competitive_races = {}
        competitive_races['all']=[]

        party_hash = {'D':'Democratic', 'R':'Republican'}

        comment_print("Dealing with jungle primary states")

        for state in ['CA', 'LA', 'WA']:
            comment_print("Dealing with state %s" % (state))
    
            races = District.objects.filter(state=state, election_year=2014)
    
            for race in races:
        
                candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True).order_by('-cash_on_hand')
                if race.office == 'H':
                    candidates = candidates.filter(Q(total_receipts__gte=house_fundraising_threshold,cash_on_hand__gte=house_cash_on_hand_threshold)|Q(is_incumbent=True))
                else:
                    candidates = candidates.filter(Q(total_receipts__gte=senate_fundraising_threshold,cash_on_hand__gte=senate_cash_on_hand_threshold)|Q(is_incumbent=True))
            


                # There are two berths, so its competitive only if there are three spots
                if len(candidates) > 2:
                    comment_print("Multiple candidates found !")
                    this_race_object = {}
                    this_race_object['race'] = race
                    this_race_object['type'] = "primary"
                    
                    
                    try:
                        primary_election = Election.objects.get(district=race, election_code='P', cycle='2014')
                        this_race_object['primary_date'] = primary_election.election_date
                        
                        # ignore primary elections that have already been held
                        if  primary_election.election_date < today:
                            try:
                                primary_runoff_election = Election.objects.get(district=race, election_code='PR', cycle='2014', election_date__gte=today)
                                this_race_object['type'] = 'primary runoff'
                                this_race_object['primary_date'] = primary_runoff_election.election_date
                                
                            except Election.DoesNotExist:
                                # No primary
                                this_race_object['primary_date']  = None
                                continue
                        
                        
                    except Election.DoesNotExist:
                        print "Missing primary election for %s" % (race)
                        continue
                    
                    this_race_object['candidates'] = []
                    print "State=%s Office =%s District =%s incumbent=%s incumbent party = %s is open %s rating: %s (%s)" % (race.state, race.office, race.office_district, race.incumbent_name, race.incumbent_party, race.open_seat,  race.rothenberg_rating_text, race.rothenberg_rating_id)
            
                    for candidate in candidates:
                        print "\tcandidate: %s party: %s incumbent: %s total raised: %s cash on hand %s (as of %s)" % (candidate.name, candidate.party, candidate.is_incumbent, candidate.total_receipts, candidate.cash_on_hand, candidate.cash_on_hand_date )
                        this_race_object['candidates'].append(candidate)
                    print "\n\n"
                    this_race_object['party']='Open*'
                    
                    
                    competitive_races['all'].append(this_race_object)
                    
                
            
    
        ## all other states
        
        races = District.objects.filter(election_year=2014).exclude(state__in=['CA', 'WA', 'LA'])

        ## manually exclude florida 13 -- we should be doing this a different way. 
        races = races.exclude(state='FL',office_district='13')

        for race in races:
    
            candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True).exclude(candidate_status__in=['W', 'LP']).order_by('-cash_on_hand')
            if race.office == 'H':
                candidates = candidates.filter(Q(total_receipts__gte=house_fundraising_threshold,cash_on_hand__gte=house_cash_on_hand_threshold)|Q(is_incumbent=True))
            else:
                candidates = candidates.filter(Q(total_receipts__gte=senate_fundraising_threshold,cash_on_hand__gte=senate_cash_on_hand_threshold)|Q(is_incumbent=True))
        
            for party in ['D', 'R']:
                party_candidates = candidates.filter(party=party)
                if len(party_candidates) > 1:
                    this_race_object = {}
                    this_race_object['race'] = race
                    this_race_object['type'] = "primary"
                    this_race_object['candidates'] = []
                    
                    try:
                        primary_election = Election.objects.get(district=race, election_code='P', cycle='2014')
                        this_race_object['primary_date'] = primary_election.election_date
                        
                        # ignore primary elections that have already been held
                        if  primary_election.election_date < today:
                            try:
                                primary_runoff_election = Election.objects.get(district=race, election_code='PR', cycle='2014', election_date__gte=today)
                                this_race_object['type'] = 'primary runoff'
                                this_race_object['primary_date'] = primary_runoff_election.election_date
                            except Election.DoesNotExist:
                                # No primary runoff
                                continue
                            
                            
                    except Election.DoesNotExist:
                        print "Missing primary election for %s" % (race)
                        continue
                    
                    
                    
                    print "State=%s Office =%s District =%s incumbent=%s incumbent party = %s is open %s rating: %s (%s)" % (race.state, race.office, race.office_district, race.incumbent_name, race.incumbent_party, race.open_seat,  race.rothenberg_rating_text, race.rothenberg_rating_id)
            
                    for candidate in party_candidates:
                        print "\tcandidate: %s party: %s incumbent: %s total raised: %s cash on hand %s (as of %s)" % (candidate.name, candidate.party, candidate.is_incumbent, candidate.total_receipts, candidate.cash_on_hand, candidate.cash_on_hand_date )
                        this_race_object['candidates'].append(candidate)
                
                    print "\n\n"
                    this_race_object['party'] = party_hash[party] 
                    
                    competitive_races['all'].append(this_race_object)            


        races = sorted(competitive_races['all'], key=lambda x: (x['primary_date'], x['race'].office_district ))
        print races
        update_time = datetime.now()
        c = Context({"update_time": update_time, "races": races})
        this_template = get_template('generated_pages/primary_list.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/primary_content.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()