from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Sum, Count, Q

from datetime import datetime, date


PROJECT_ROOT = settings.PROJECT_ROOT


CYCLE_START = date(2013,1,1)

# really about setting losers, but... 


from django.core.management.base import BaseCommand, CommandError
from summary_data.data_references import CANDIDATE_STATUS_CHOICES, CANDIDATE_STATUS_DICT, COMPETITIVE_INDEPENDENTS

from summary_data.models import Committee_Overlay, Candidate_Overlay, District


status_array = CANDIDATE_STATUS_DICT.keys()
chambers = [{'name':'Senate', 'value':'S'}, {'name':'House', 'value':'H'}]

rothenberg_classes = [
{'id':1,'name':'Safe Democrat, Democrat Favored', 'values':[4,5], 'assigned_party':'D', 'display':'none'},
{'id':2,'name':'Lean Democrat', 'values':[3], 'assigned_party':'D', 'display':'none'},
{'id':3,'name':'Toss-up/Tilt Democrat', 'values':[2], 'assigned_party':None, 'display':'block'},
{'id':4,'name':'Tossup', 'values':[1], 'assigned_party':None, 'display':'block'},
{'id':5,'name':'Toss-up/Tilt Republican', 'values':[6], 'assigned_party':None, 'display':'block'},
{'id':6,'name':'Lean Republican', 'values':[7], 'assigned_party':'R', 'display':'none'},
{'id':7,'name':'Safe Republican, Republican Favored', 'values':[8,9], 'assigned_party':'R', 'display':'none'},
]

independent_districts = [i['district_id'] for i in COMPETITIVE_INDEPENDENTS]

def run_districts(district_queryset, queryset_name):
    print "handling %s" % (queryset_name)
    unresolved = 0
    too_many_winners = 0
    too_many_candidates = 0
    

    for district in district_queryset:
        
        
        #print "handling %s" % district
        party_list = ['D', 'R']
        if district.pk in independent_districts:
            party_list.append("I")
        #print district, rothenberg_class
    
        ## just add 'is_general_candidate=True' here to filter once we've set this stuff. 
        # candidates = all_candidates.filter(district=district).exclude(not_seeking_reelection=True)
        candidates = all_candidates = Candidate_Overlay.objects.filter(district=district, is_general_candidate=True, party__in=party_list).exclude(not_seeking_reelection=True)
    
        candidate_winners = 0
        victors = 0
        victor_array = []
        numcandidates = 0 
        for candidate in candidates:
            numcandidates += 1
            if candidate.cand_is_gen_winner:                    
                victors += 1
                victor_array.append(candidate)
    
                
        if victors==0:
            print "WARN: No winner for %s - %s" % (district, district.rothenberg_rating_text)
            unresolved += 1
            if district.general_is_decided:
                district.general_is_decided = False
                district.save()
            
            for candidate in Candidate_Overlay.objects.filter(district=district):
                if not candidate.cand_is_gen_winner == None:
                    candidate.cand_is_gen_winner = None
                    candidate.save()
            
        if victors > 1:
            print "WARN: More than one winner for %s - %s" % (district, district.rothenberg_rating_text)
            too_many_winners += 1
            for this_victor in victor_array:
                print this_victor
            
            print "\t\tMarking this race as undecided until this is fixed!!!"
            if district.general_is_decided:
                district.general_is_decided = False
                district.save()
            
            for candidate in Candidate_Overlay.objects.filter(district=district):
                if not candidate.cand_is_gen_winner == None:
                    candidate.cand_is_gen_winner = None
                    candidate.save()
    
        if numcandidates > 2:
            print "WARN: more than two candidates found for  %s - %s" % (district, district.rothenberg_rating_text)
            too_many_candidates += 1
        
        # now clean up the district -- mark that it's decided 
        if victors==1:
            if not district.general_is_decided:
                district.general_is_decided = True
                district.save()
            for candidate in Candidate_Overlay.objects.filter(district=district):
                if not candidate.cand_is_gen_winner:
                    candidate.cand_is_gen_winner = False
                    candidate.save()
        
        
    print "\n\n---------------\n"
    print "Summary of %s " % (queryset_name)
    print "%s districts with no winner" % (unresolved)
    print "%s districts with more than 1 winner" % (too_many_winners)
    print "%s districts with more than two general candidates--this may be legitimate, but usually aren't" % (too_many_candidates)
    print "\n---------------\n"
    
    

class Command(BaseCommand):
    help = "Set general election status"
    requires_model_validation = False
    
    status_list =  CANDIDATE_STATUS_DICT.keys()
    
    def handle(self, *args, **options):
        today = date.today()
        update_time = datetime.now()
        
        
        # if there's an existing candidate status, they didn't win. 
        house_districts = District.objects.filter(office='H').order_by('office', 'office_district')
        senate_districts = chamber_districts = District.objects.filter(office='S').filter(Q(term_class=2)|Q(id__in=[1003, 1053, 1061]))
        
        results = []
        
        run_districts(senate_districts, 'SENATE')        
        run_districts(house_districts, 'HOUSE')


                                       
            
