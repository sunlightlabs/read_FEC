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

class Command(BaseCommand):
    help = "Set general election status"
    requires_model_validation = False
    
    status_list =  CANDIDATE_STATUS_DICT.keys()
    
    def handle(self, *args, **options):
        today = date.today()
        update_time = datetime.now()
        
        
        # if there's an existing candidate status, they didn't win. 
        all_candidates = Candidate_Overlay.objects.all()
        all_districts = District.objects.all().order_by('office', 'office_district')
        
        results = []
        


        for district in all_districts:
            #print "handling %s" % district
            party_list = ['D', 'R']
            if district.pk in independent_districts:
                party_list.append("I")
            #print district, rothenberg_class
            
            ## just add 'is_general_candidate=True' here to filter once we've set this stuff. 
            # candidates = all_candidates.filter(district=district).exclude(not_seeking_reelection=True)
            candidates = all_candidates.filter(district=district, is_general_candidate=True, party__in=party_list).exclude(not_seeking_reelection=True)
            
            candidate_winners = 0
            victors = 0
            numcandidates = 0 
            for candidate in candidates:
                numcandidates += 1
                if candidate.cand_is_gen_winner:                    
                    victors += 1
            
            if victors==0:
                print "WARN: No winner for %s" % district
            if victors > 0:
                print "WARN: More than one winner for %s" % district
            
            if numcandidates > 2:
                print "WARN: more than two candidates found for %s" % district
                                       
            
