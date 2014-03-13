from datetime import date
from django.core.management.base import BaseCommand, CommandError
 

election_day_2014 = date(2014,11,4)
cycle_start = date(2013,1,1)
today = date.today()

from summary_data.models import *
from summary_data.election_dates import election_dates_2014


def update_races():
    # set the next election dates -- this should be run daily I guess
    races_2014 = District.objects.filter(election_year=2014)
    for district in races_2014:
        print "handling race %s" % (district)
        # Get all elections
        elections = Election.objects.filter(district=district).order_by('election_date')
        for election in elections:
            if election.election_date >= today:
                print election.election_date, election.election_code
                district.next_election_date = election.election_date
                district.next_election_code = election.election_code
                # throw the 'special election scheduled' flag if the next election is a special election
                special_scheduled = False
                if election.election_code in ['SP', 'OR', 'SG', 'SR']:
                    special_scheduled = True
                
                district.special_election_scheduled = special_scheduled
                
                district.save()
                # We're done
                break

def create_needed_primary_runoffs():
    # create any runoff elections on the basis of the 'primary runoff needed' part of the district page
    # this is human adminned.
    # only works for normal elections.
    
    runoffs_needed_elections = ElectionSummary.objects.filter(primary_runoff_needed=True, election_summary_code='N')
    for election in runoffs_needed_elections:
        state = election.district.state
        if election_dates_2014[state]['has_runoff'] == 0:
            print "No primary runoff date available for %s" % (state)
            continue
        
        obj, created = Election.objects.get_or_create(district=election.district, election=election, election_code='PR',
            defaults={
                'cycle':'2014',
                'election_year':2014,
                'election_date':election_dates_2014[state]['runoff'],                    
            })
    

class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        create_needed_primary_runoffs()        
        update_races()
        

        
        
        