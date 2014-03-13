from datetime import date
from django.core.management.base import BaseCommand, CommandError
 

election_day_2014 = date(2014,11,4)
cycle_start = date(2013,1,1)
today = date.today()

from summary_data.models import *
from summary_data.election_dates import election_dates_2014, special_house_elections, special_senate_elections




class Command(BaseCommand):
 
    def handle(self, *args, **options): 
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
                    district.save()
                    # We're done
                    break