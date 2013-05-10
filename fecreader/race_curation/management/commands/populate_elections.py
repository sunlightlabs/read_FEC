from django.core.management.base import BaseCommand, CommandError

# Creates races from districts, and from special elections 

from race_curation.utils.senate_crosswalk import senate_crosswalk
from race_curation.utils.house_crosswalk import house_crosswalk
from race_curation.models import District, Election, Candidate_Overlay, Election_Candidate
from legislators.models import Legislator, Term
from race_curation.utils.session_data import senate_special_elections, house_special_elections


def pop_house_elections():
    # get all house districts
    cycle = '2014'
    house_districts = District.objects.filter(office='H')
    
    # make regularly scheduled elections
    for hd in house_districts:
        for election_code in ['P', 'G']:
            # make primary and general elections for 2014 cycle:
            if election_code == 'P':
                for primary_party in ['D', 'R']:
                    election, created = Election.objects.get_or_create(district=hd, cycle=cycle, election_year=2014, open_seat=hd.open_seat, incumbent_name=hd.incumbent_name, incumbent_pty=hd.incumbent_pty, incumbent_party=hd.incumbent_party, state=hd.state, office='H', office_district=hd.office_district, election_code=election_code, primary_party=primary_party)

            else:
                election, created = Election.objects.get_or_create(district=hd, cycle=cycle, election_year=2014, open_seat=hd.open_seat, incumbent_name=hd.incumbent_name, incumbent_pty=hd.incumbent_pty, incumbent_party=hd.incumbent_party, state=hd.state, office='H', office_district=hd.office_district, election_code=election_code)

    # add special elections
    for se in house_special_elections:
        hd= District.objects.get(state=se['state'], office_district=se['office_district'], office='H')
        primary_party = None
        try:
            primary_party=se['primary_party']
        except KeyError:
            pass
            
        election, created = Election.objects.get_or_create(district=hd, cycle=cycle, election_year=se['election_year'], election_date=se['election_date'], open_seat=hd.open_seat, incumbent_name=hd.incumbent_name, incumbent_pty=hd.incumbent_pty, incumbent_party=hd.incumbent_party, state=hd.state, office='H', office_district=hd.office_district, election_code=se['election_code'], primary_party=primary_party)
        
def pop_senate_elections():
    # get all house districts

    senate_districts = District.objects.filter(office='S')

    # make regularly scheduled elections
    for sd in senate_districts:
        for election_code in ['P', 'G']:
            if election_code == 'P':
                for primary_party in ['D', 'R']:
                    election, created = Election.objects.get_or_create(district=sd, cycle=sd.cycle, election_year=sd.election_year, open_seat=sd.open_seat, incumbent_name=sd.incumbent_name, incumbent_pty=sd.incumbent_pty, incumbent_party=sd.incumbent_party, state=sd.state, office='S', term_class=sd.term_class, election_code=election_code, primary_party=primary_party)
            else:
                election, created = Election.objects.get_or_create(district=sd, cycle=sd.cycle, election_year=sd.election_year, open_seat=sd.open_seat, incumbent_name=sd.incumbent_name, incumbent_pty=sd.incumbent_pty, incumbent_party=sd.incumbent_party, state=sd.state, office='S', term_class=sd.term_class, election_code=election_code)

    # add special elections
    for se in senate_special_elections:
        primary_party=None
        try:
            primary_party=se['primary_party']
        except KeyError:
            pass
        
        sd= District.objects.get(state=se['state'], term_class=se['term_class'], office='S')
        election, created = Election.objects.get_or_create(district=sd, cycle=se['cycle'], election_year=se['election_year'], election_date=se['election_date'], open_seat=sd.open_seat, incumbent_name=sd.incumbent_name, incumbent_pty=sd.incumbent_pty, incumbent_party=sd.incumbent_party, state=sd.state, office='S', term_class=se['term_class'], election_code=se['election_code'], primary_party=primary_party)
        

def populate_primary_election_candidates():
    elections = Election.objects.filter(election_code='P')
    for election in elections:
        district = election.district
        print "election %s district: %s" % (election, district)
        candidates = Candidate_Overlay.objects.filter(district=district, party=election.primary_party, election_year=election.election_year)
        for candidate in candidates:
            print "Found primary candidate %s" % candidate
            ec, created = Election_Candidate.objects.get_or_create(candidate=candidate, race=election)

class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        pop_house_elections()
        pop_senate_elections() 
        populate_primary_election_candidates()
               