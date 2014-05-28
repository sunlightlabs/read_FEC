# check a state to see if candidate statuses have been set after a primary. Warns about too many candidates remaining in a race. 


from optparse import make_option

from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Q

from summary_data.models import District, Candidate_Overlay, Election

from django.core.management.base import BaseCommand, CommandError

today = date.today()


def comment_print(message):
    print "###  " + message + "\n"
    
########
# Deal with jungle primary states first: CA, WA, LA
########


class Command(BaseCommand):
    help = "Regenerate the static competitive primary page."
    requires_model_validation = False
    
    
    option_list = BaseCommand.option_list + (
            make_option('--state',
                        action='store',
                        dest='state',
                        help="State to process"),
            )
    
    def handle(self, *args, **options):

        state = options['state']
        assert state, "No state given"
        print "Checking primary for state='%s'" % (state)

        if state in ['CA', 'LA', 'WA']:
            comment_print("Dealing with state %s" % (state))
    
            races = District.objects.filter(state=state, election_year=2014)
    
            for race in races:
                #print "Handling race %s" % (race)
        
                candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True, candidate_status__in=['W', 'LP', 'SP', 'SR', 'SG', 'SX']).order_by('-cash_on_hand')
                

                # There are two berths, so its competitive only if there are three spots
                if len(candidates) > 2:
                    comment_print("Too many candidates remaining in jungle primary: %s %s %s" % (state, race.office, race.office_district))
                    


        else:
            
            races = District.objects.filter(election_year=2014, state=state)

            
            for race in races:
                #print "Handling race %s" % (race)
                
                for party in ['D', 'R']:
                    candidates = Candidate_Overlay.objects.filter(district=race, party=party).exclude(not_seeking_reelection=True, candidate_status__in=['W', 'LP', 'SP', 'SR', 'SG', 'SX']).order_by('-cash_on_hand')
                    if len(candidates) > 1:
                        print "Too many candidates still in race after %s primary: %s %s %s" % (party, state, race.office, race.office_district)    
                        for candidate in candidates:
                            print "\t%s %s %s %s %s" % (candidate.name, candidate.fec_id, candidate.office, candidate.office_district, candidate.party)
            