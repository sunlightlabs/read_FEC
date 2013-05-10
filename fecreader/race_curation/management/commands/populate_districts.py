#  populate the districts from the us congress list. This just creates the districts -- it doesn't populate the incumbents. 

from django.core.management.base import BaseCommand

from race_curation.models import *
from race_curation.utils.term_reference import get_election_year_from_term_class
from legislators.models import Legislator, Term
from legislators.congresses import congress_dates
from datetime import date
from race_curation.utils.party_reference import get_party_from_pty, get_party_from_term_party
from race_curation.utils.session_data import senate_special_elections, house_special_elections

today = date.today()
cycle = '2014'
cycle_start = date(2013,1,5)
cycle_end = date(2014,12,31)
def create_house_districts():
    # pull this from us_congress repo data--which is in the legislators app
    
    house_districts = Term.objects.filter(start__lte=cycle_end, end__gte=cycle_start, term_type='rep').order_by('state', 'district')
    unique_hd = house_districts.values('state', 'district').distinct()
    for d in unique_hd:
        print d
        district_fixed = d['district'].zfill(2)
        thisdistrict, created = District.objects.get_or_create(cycle=cycle,state=d['state'], office='H', office_district=district_fixed, election_year='2014')
        
        incumbent_term = Term.objects.filter(start__lte=cycle_end, end__gte=cycle_start, term_type='rep', district=d['district'], state=d['state']).order_by('-start')[0]
        party = get_party_from_term_party(incumbent_term.party)
        name = incumbent_term.legislator.official_full
        thisdistrict.incumbent_party = party
        thisdistrict.incumbent_legislator = incumbent_term.legislator
        thisdistrict.incumbent_name = name
        thisdistrict.save()

def create_senate_districts():
    # pull this from us_congress repo data--which is in the legislators app

    senate_districts = Term.objects.filter(start__lte=cycle_end, end__gte=cycle_start, term_type='sen').order_by('state', 'term_class')
    unique_sd = senate_districts.values('state', 'term_class').distinct()
    for s in unique_sd:
        term_class = s['term_class']
        election_year = get_election_year_from_term_class(term_class)
        election_cycle = str(election_year)
        print s
        thisdistrict, created = District.objects.get_or_create(cycle=election_cycle,state=s['state'], office='S', term_class=s['term_class'], election_year = election_year)
        
        incumbent_term = Term.objects.filter(start__lte=cycle_end, end__gte=cycle_start, term_type='sen', term_class = s['term_class'], state=s['state']).order_by('-start')[0]
        party = get_party_from_term_party(incumbent_term.party)
        name = incumbent_term.legislator.official_full
        thisdistrict.incumbent_party = party
        thisdistrict.incumbent_legislator = incumbent_term.legislator
        thisdistrict.incumbent_name = name
        thisdistrict.save()
        
def set_house_special_elections():
    for se in house_special_elections:
        # we assume that special elections are in real districts; we use get_or_create because incumbents are sometimes missing.
        this_district, created = District.objects.get_or_create(state=se['state'], office_district=se['office_district'], office='H')
        this_district.special_election_scheduled = True
        if se['election_date'] >= today:
            if this_district.next_election_date:
                if se['election_date'] < this_district.next_election_date:
                    this_district.next_election_date = se['election_date']
                    this_district.next_election_code = se['election_code']
                    this_district.election_year = se['election_year']
            else:            
                this_district.next_election_date = se['election_date']
                this_district.next_election_code = se['election_code']
                this_district.election_year = se['election_year']
        # a few saves aren't needed, but this isn't exactly burdensome        
        this_district.save()
                


def set_senate_special_elections():
    for se in senate_special_elections:
        # we assume that special elections are in real districts; we use get_or_create because incumbents are sometimes missing.
        this_district = District.objects.get(state=se['state'], term_class=se['term_class'], office='S')
        this_district.special_election_scheduled = True
        if se['election_date'] >= today:
            if this_district.next_election_date:
                if se['election_date'] < this_district.next_election_date:
                    this_district.next_election_date = se['election_date']
                    this_district.next_election_code = se['election_code']
                    this_district.election_year = se['election_year']
            else:            
                this_district.next_election_date = se['election_date']
                this_district.next_election_code = se['election_code']
                this_district.election_year = se['election_year']
        # a few saves aren't needed, but this isn't exactly burdensome        
        this_district.save()


class Command(BaseCommand):
    def handle(self, *args, **options): 
        create_house_districts()
        create_senate_districts()
        set_house_special_elections()
        set_senate_special_elections()

