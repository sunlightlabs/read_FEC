from django.core.management.base import BaseCommand, CommandError

# Creates races from districts, and from special elections 

from summary_data.utils.senate_crosswalk import senate_crosswalk
from summary_data.utils.house_crosswalk import house_crosswalk
from summary_data.models import *
from legislators.models import Legislator, Term
from summary_data.utils.session_data import senate_special_elections, house_special_elections


def pop_house_elections():
    # get all house districts
    cycle = '2014'
    house_districts = District.objects.filter(office='H')
    
    # make regularly scheduled elections
    for hd in house_districts:
        this_election, created = Election.objects.get_or_create(district=hd, cycle=cycle, election_year=2014, open_seat=hd.open_seat, incumbent_name=hd.incumbent_name, incumbent_pty=hd.incumbent_pty, incumbent_party=hd.incumbent_party, state=hd.state, office='H', office_district=hd.office_district, election_code='N')
        
        for election_code in ['P', 'G']:
            # make primary and general elections for 2014 cycle:
            if election_code == 'P':
                for primary_party in ['D', 'R']:
                    subelection, created = SubElection.objects.get_or_create(parentElection=this_election, primary_party=primary_party, subelection_code='P')

            else:
                subelection, created = SubElection.objects.get_or_create(parentElection=this_election, subelection_code='G')

    # add special elections
    for se in house_special_elections:
        hd= District.objects.get(state=se['state'], office_district=se['office_district'], office='H')
        primary_party = se.get('primary_party')
        election, created = Election.objects.get_or_create(district=hd, cycle=cycle, election_year=se['election_year'], open_seat=hd.open_seat, incumbent_name=hd.incumbent_name, incumbent_pty=hd.incumbent_pty, incumbent_party=hd.incumbent_party, state=hd.state, office='H', office_district=hd.office_district, election_code='S')
            
        subelection, created = SubElection.objects.get_or_create(parentElection=election, primary_party=primary_party, subelection_code=se['election_code'], election_date=se['election_date'])
        
        
def pop_senate_elections():
    # get all senate districts

    senate_districts = District.objects.filter(office='S')

    # make regularly scheduled elections
    for sd in senate_districts:
        this_election, created = Election.objects.get_or_create(district=sd, cycle=sd.cycle, election_year=sd.election_year, open_seat=sd.open_seat, incumbent_name=sd.incumbent_name, incumbent_pty=sd.incumbent_pty, incumbent_party=sd.incumbent_party, state=sd.state, office='S', term_class=sd.term_class, election_code='N')
        
        for election_code in ['P', 'G']:
            if election_code == 'P':
                for primary_party in ['D', 'R']:
                    subelection, created = SubElection.objects.get_or_create(parentElection=this_election, primary_party=primary_party, subelection_code='P')
                    
            else:
                subelection, created = SubElection.objects.get_or_create(parentElection=this_election, subelection_code='G')

    # add special elections
    for se in senate_special_elections:
        primary_party=se.get('primary_party')

        
        sd= District.objects.get(state=se['state'], term_class=se['term_class'], office='S')
        election, created = Election.objects.get_or_create(district=sd, cycle=se['cycle'], election_year=se['election_year'], open_seat=sd.open_seat, incumbent_name=sd.incumbent_name, incumbent_pty=sd.incumbent_pty, incumbent_party=sd.incumbent_party, state=sd.state, office='S', term_class=se['term_class'], election_code='S')
        subelection, created = SubElection.objects.get_or_create(parentElection=election, primary_party=primary_party, subelection_code=se['election_code'], election_date=se['election_date'])

def populate_election_candidates():
    # Doesn't handle special elections
    elections = Election.objects.filter(election_code='N')
    for election in elections:
        district = election.district
        print "election %s district: %s" % (election, district)
        candidates = Candidate_Overlay.objects.filter(district=district, election_year=election.election_year)
        for candidate in candidates:
            print "Found candidate %s" % candidate
            ec, created = Election_Candidate.objects.get_or_create(candidate=candidate, race=election)

class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        pop_house_elections()
        pop_senate_elections() 
        populate_election_candidates()
               