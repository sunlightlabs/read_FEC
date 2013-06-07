# first make candidates from incumbents; then add candidates from fec filings.
# need to curate retiring folks... 

from django.core.management.base import BaseCommand, CommandError

# start with the list of known incumbents from the senate crosswalk. 

from race_curation.utils.senate_crosswalk import senate_crosswalk
from race_curation.utils.house_crosswalk import house_crosswalk
from race_curation.utils.party_reference import get_party_from_pty

from legislators.models import Legislator, Term

# retirement list
from race_curation.utils.session_data import senate_casualties_2014, house_casualties_2014, senate_exclusions_2014

from race_curation.utils.term_reference import get_election_year_from_term_class, get_term_class_from_election_year

from ftpdata.models import Candidate
from race_curation.models import Candidate_Overlay, District

from datetime import datetime

today = datetime.today()

cycle_start = datetime(2013,1,5)
cycle_end = datetime(2014,12,31)
cycle = '2014'

# Hash the fec ids of retiring folks
senate_casualty_hash = {}
for s in senate_casualties_2014:
    senate_casualty_hash[s['fec_id']]=s['name']
    
house_casualty_hash = {}
for h in house_casualties_2014:
    house_casualty_hash[h['fec_id']]=h['name']

senate_exclusion_hash = {}
for s in senate_exclusions_2014:
    senate_exclusion_hash[s['fec_id']]=s['name']
    
house_exclusion_hash = {}
# don't have one yet

def get_house_incumbents():
    # Get the incumbents
    for member in house_crosswalk:
        bio = member['bioguide']
        fec_id = member['fec_id']

        thiscandidate = Candidate.objects.get(cand_id=fec_id, cycle=cycle)
        office = thiscandidate.cand_office
        district = None

        district = thiscandidate.cand_office_district.zfill(2)
        state = thiscandidate.cand_office_st

        #print "processing %s: %s %s %s" % (thiscandidate.cand_name, office, state, district)
        this_district = District.objects.get(cycle=cycle,state=state, office='H', office_district=district)


        this_overlay, created = Candidate_Overlay.objects.get_or_create(fec_id=fec_id, cycle=cycle, district=this_district)
        this_overlay.name = thiscandidate.cand_name
        this_overlay.pty = thiscandidate.cand_pty_affiliation
        this_overlay.party = get_party_from_pty(thiscandidate.cand_pty_affiliation)
        this_overlay.pcc = thiscandidate.cand_pcc
        this_overlay.cand_ici = 'I'
        this_overlay.election_year = 2014
        this_overlay.save()
        
        try:
            house_casualty_hash[fec_id]
            this_overlay.not_seeking_reelection = True
            this_overlay.save()
            this_district.open_seat = True
            this_district.save()
            
        except KeyError:
            pass

def get_house_challengers():        
    # then get the candidates who are declared. While we set the incumbents' election year as 2014--overriding whatever they have in their FEC filings, we don't do that here. 
    allHouseCandidates = Candidate.objects.filter(cycle=cycle, cand_office='H', cand_election_year=2014)
    for thiscandidate in allHouseCandidates:
        fec_id = thiscandidate.cand_id
        try:
            house_exclusion_hash[fec_id]
            continue
        except KeyError:
            pass
        #print "handling %s" % (thiscandidate.cand_name)
        # do we already have this candidate entered ? 
        try:
            entered_candidate = Candidate_Overlay.objects.get(election_year=2014, fec_id=fec_id)
            #print "Found candidate %s status %s" % (entered_candidate.name, entered_candidate.cand_ici)
        except Candidate_Overlay.DoesNotExist:
            # don't enter if they say they're an incumbent. Problaby an error. 
            if thiscandidate.cand_ici == 'I':
                print "!! Not-yet-entered House candidate %s %s %s claims incumbency. Perhaps they've retired?" % (thiscandidate.cand_name, thiscandidate.cand_office_district, thiscandidate.cand_office_st)
            else:
                # It's a new candidate. Enter it.

                if not thiscandidate.cand_office_district:
                    print "!!Missing district!! %s %s" % (thiscandidate.cand_name, fec_id)
                    continue

                district = thiscandidate.cand_office_district.zfill(2)
                state = thiscandidate.cand_office_st


                try:
                    this_district = District.objects.get(cycle=cycle,state=state, office='H', office_district=district, election_year=thiscandidate.cand_election_year)
                    
                    # Only make it an open seat if we've already marked the district as open.
                    cand_ici = 'C'
                    if this_district.open_seat:
                        cand_ici='O'
                        
                    Candidate_Overlay.objects.create(
                        district=this_district,
                        cycle=cycle,
                        fec_id=fec_id,
                        name=thiscandidate.cand_name,
                        pty=thiscandidate.cand_pty_affiliation,
                        party = get_party_from_pty(thiscandidate.cand_pty_affiliation),
                        pcc=thiscandidate.cand_pcc,
                        election_year=thiscandidate.cand_election_year,
                        state=thiscandidate.cand_office_st,
                        office='H',
                        office_district=thiscandidate.cand_office_district,
                        cand_ici=cand_ici,
                        candidate_status='D'
                    )
                except District.DoesNotExist:
                    print "!! Invalid district for %s %s %s" % (thiscandidate.cand_name, district, state)
                    continue

                #print "Entering %s with status %s" % (thiscandidate.cand_name, thiscandidate.cand_ici)
                

def get_senate_incumbents():
    # Get the incumbents
    for member in senate_crosswalk:
        bio = member['bioguide']
        fec_id = member['fec_id']
        
        if not fec_id:
            # ignore 
            continue
        #print "handling %s %s" % (bio, fec_id)
        # term class isn't kept in the fec records...
        
        
        thisterm = Term.objects.get(start__lte=cycle_end, end__gte=cycle_start, term_type='sen', legislator__bioguide=bio)
        
        thiscandidate = Candidate.objects.get(cand_id=fec_id, cycle=cycle)
        office = thiscandidate.cand_office
        term_class = thisterm.term_class
        state = thiscandidate.cand_office_st

        #print "processing %s: %s %s %s" % (thiscandidate.cand_name, office, state, term_class)
        election_year = get_election_year_from_term_class(term_class)
        senate_cycle = str(election_year)
        this_district = District.objects.get(cycle=senate_cycle,state=state, office='S', term_class=term_class)


        this_overlay, created = Candidate_Overlay.objects.get_or_create(fec_id=fec_id, cycle=senate_cycle, district=this_district)
        this_overlay.name = thiscandidate.cand_name
        this_overlay.candidate = thiscandidate
        this_overlay.office='S'
        this_overlay.state = thiscandidate.cand_office_st
        this_overlay.pty = thiscandidate.cand_pty_affiliation
        this_overlay.party = get_party_from_pty(thiscandidate.cand_pty_affiliation)        
        this_overlay.pcc = thiscandidate.cand_pcc
        this_overlay.cand_ici = 'I'
        this_overlay.election_year = election_year
        this_overlay.term_class=term_class
        this_overlay.save()

        try:
            senate_casualty_hash[fec_id]
            this_overlay.not_seeking_reelection = True
            this_overlay.save()
            this_district.open_seat = True
            this_district.save()

        except KeyError:
            pass

def get_senate_challengers():        
    # then get the candidates who are declared. While we set the incumbents' election year as 2014--overriding whatever they have in their FEC filings, we don't do that here. 
    allSenateCandidates = Candidate.objects.filter(cycle=cycle, cand_office='S', cand_election_year__gte=2013)
    for thiscandidate in allSenateCandidates:
        fec_id = thiscandidate.cand_id
        
        try:
            senate_exclusion_hash[fec_id]
            continue
        except KeyError:
            pass
        
        #print "handling %s" % (thiscandidate.cand_name)
        # do we already have this candidate entered ? 
        try:
            entered_candidate = Candidate_Overlay.objects.get(election_year__gte=2013, fec_id=fec_id)
            #print "Found candidate %s status %s" % (entered_candidate.name, entered_candidate.cand_ici)
        except Candidate_Overlay.DoesNotExist:
            # don't enter if they say they're an incumbent. Problaby an error. 
            if thiscandidate.cand_ici == 'I':
                print "!! Not-yet-entered Senate candidate %s %s %s claims incumbency. Perhaps they've retired?" % (thiscandidate.cand_name, thiscandidate.cand_election_year, thiscandidate.cand_office_st)
            else:
                # It's a new candidate. Enter it.

                state = thiscandidate.cand_office_st
                term_class = get_term_class_from_election_year(thiscandidate.cand_election_year)
                if thiscandidate.cand_election_year < 2013:
                    print "!! Disregarding old candidate %s %s %s" % (thiscandidate.cand_name, thiscandidate.cand_election_year, state)
                
                election_year = str(thiscandidate.cand_election_year)


                try:
                    this_district = District.objects.get(election_year=election_year, state=state, office='S')

                    # Only make it an open seat if we've already marked the district as open.
                    cand_ici = 'C'
                    if this_district.open_seat:
                        cand_ici='O'

                    Candidate_Overlay.objects.create(
                        district=this_district,
                        cycle=cycle,
                        fec_id=fec_id,
                        name=thiscandidate.cand_name,
                        pty=thiscandidate.cand_pty_affiliation,
                        party = get_party_from_pty(thiscandidate.cand_pty_affiliation),
                        #pcc=thiscandidate.cand_pcc,
                        term_class=term_class,
                        election_year=thiscandidate.cand_election_year,
                        state=thiscandidate.cand_office_st,
                        office='S',
                        cand_ici=cand_ici,
                        candidate_status='D'
                    )
                except District.DoesNotExist:
                    print "!! Invalid senate district for %s %s %s %s" % (thiscandidate.cand_name, term_class, thiscandidate.cand_election_year, state)
                    continue

                #print "Entering %s with status %s" % (thiscandidate.cand_name, thiscandidate.cand_ici)

def run_house():
    get_house_incumbents()
    get_house_challengers()
    
def run_senate():
    get_senate_incumbents()
    get_senate_challengers()    

class Command(BaseCommand):
 
    def handle(self, *args, **options): 
        run_house()
        run_senate()
