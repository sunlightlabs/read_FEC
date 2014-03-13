""" Ugliness to create elections; there are tons of special cases. In general we don't create runoffs here, only record the dates they might happen, since they only take place if needed. Which is something we might wanna just ignore. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
 

election_day_2014 = date(2014,11,4)
cycle_start = date(2013,1,1)

from summary_data.models import *
from summary_data.election_dates import election_dates_2014, special_house_elections, special_senate_elections

def pop_normal_elections():
    districts = District.objects.filter(election_year=2014).exclude(state__in=['AS', 'GU', 'PR', 'VI', 'MP'])
    for d in districts:
        this_state = d.state
        state_data = election_dates_2014[this_state]
        print this_state, state_data
        has_primary_runoff = False
        primary_runoff_date = None
        has_general_runoff = False
        general_runoff_date = None
        if state_data['has_runoff'] == 1:
            has_primary_runoff = True
            primary_runoff_date = state_data['runoff']
        
        if this_state in ['LA', 'GA']:
            has_general_runoff = True
            if this_state == 'LA':
                general_runoff_date = date(2014,12,6)
            else:
                # How can georgia hold a general runoff election after the date that reps would be sworn in? 
                # See court order:
                # http://www.scribd.com/doc/163441428/Court-Order-Regarding-Georgia-2014-Election-Calendar-changes
                # This would require a third candidate getting a sizeable chunk of the vote, so it's not a likely outcome, I guess
                general_runoff_date = date(2015,1,6)
        
        election_summary, created = ElectionSummary.objects.get_or_create(district=d, election_summary_code='N', defaults={
        'cycle':'2014',
        'election_year':2014,
        'election_date':election_day_2014,
        })
        # now create the primary and general elections
        
        # the start date for the general election is the primary. But this might be wrong if there is a runoff. 
        # We don't yet know whether there *will* be a runoff. 
        
        for election_code in ['P', 'G']:
            print election_code

            if election_code == 'P':
                if this_state == 'LA':
                    continue
                start_date = cycle_start
                election_date = state_data['primary']
                
            else:
                if this_state == 'LA':
                    start_date = cycle_start
                else:
                    start_date = state_data['primary']
                election_date = election_day_2014
            obj, created = Election.objects.get_or_create(district=d, election=election_summary, election_code=election_code,
                defaults={
                    'cycle':'2014',
                    'election_year':2014,
                    'start_date':start_date,
                    'election_date':election_date,                    
                })
    
def process_special_election(election, chamber):
    district = None
    this_state = election['state']

    try:
        if chamber=='H':
            district = District.objects.get(state=election['state'], office_district=election['district'], office=chamber)
        else:
            district = District.objects.get(state=election['state'], term_class=election['term_class'], office=chamber)
    except District.DoesNotExist:
        print "**** Missing district: %s" % election
        return None


    print "Creating election summary %s, %s" % (this_state, election)
    
    election_summary, created = ElectionSummary.objects.get_or_create(district=district, election_summary_code='S', defaults={
        'cycle':'2014',
        'election_year':2014,
        'election_date':election_day_2014,
    })
    # now create the primary and general elections
    # Give up on election start dates. It's a mess for these. 
    # Will be added in a subsequent script. 
    
    for key in election['elections']:
        election_code = key
        election_date = election['elections'][key]
        if key not in ['P', 'G']:
            continue
        
        print election_code, election_date
        election_date = election_date
        
        # these files use P for primary -- but that's really a special primary; ditto for G -> SG
        if election_code == 'P':
            election_code = 'SP'
        if election_code == 'G':
            election_code = 'SG'
        
        obj, created = Election.objects.get_or_create(district=district, election=election_summary, election_code=election_code,
            defaults={
                'cycle':'2014',
                'election_year':2014,
                'election_date':election_date,
            })

def pop_special_elections():
    for election in special_house_elections:
        process_special_election(election, 'H')
    for election in special_senate_elections:
        process_special_election(election, 'S')



class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        pop_normal_elections()
        pop_special_elections()
