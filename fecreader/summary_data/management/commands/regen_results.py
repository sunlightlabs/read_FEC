# really about setting losers, but... 

from datetime import date

from django.core.management.base import BaseCommand, CommandError
from summary_data.data_references import CANDIDATE_STATUS_CHOICES, CANDIDATE_STATUS_DICT, COMPETITIVE_INDEPENDENTS

from summary_data.models import Committee_Overlay, Candidate_Overlay, District


status_array = CANDIDATE_STATUS_DICT.keys()
chambers = [{'name':'House', 'value':'H'}, {'name':'Senate', 'value':'S'}]

rothenberg_classes = [
{'name':'Safe Democrat, Democrat Favored', 'values':[4,5], 'assigned_party':'D'},
{'name':'Lean Democrat', 'values':[3], 'assigned_party':'D'},
{'name':'Toss-up/Tilt Democrat', 'values':[2], 'assigned_party':None},
{'name':'Tossup', 'values':[1], 'assigned_party':None},
{'name':'Toss-up/Tilt Republican', 'values':[6], 'assigned_party':None},
{'name':'Lean Republican', 'values':[7], 'assigned_party':'R'},
{'name':'Safe Republican, Republican Favored', 'values':[8,9], 'assigned_party':'R'},
]

independent_districts = [i['district_id'] for i in COMPETITIVE_INDEPENDENTS]

class Command(BaseCommand):
    help = "Set general election status"
    requires_model_validation = False
    
    status_list =  CANDIDATE_STATUS_DICT.keys()
    
    def handle(self, *args, **options):
        today = date.today()
        
        # if there's an existing candidate status, they didn't win. 
        all_candidates = Candidate_Overlay.objects.all()
        all_districts = District.objects.all()
        
        results_dict = {}
        
        for chamber in chambers:
            chamber_candidates = all_candidates.filter(office=chamber['name'])
            chamber_districts = all_districts.filter(office=chamber['value'])
            
            if chamber['value'] == 'S':
                # there are 3 class 3 special elections here too, I believe... 
                chamber_districts = chamber_districts.filter(term_class=2)
                
            results_dict[chamber['name']] = []

            for rothenberg_class in rothenberg_classes:
                class_dict[rothenberg_class['name']] = []
                
                districts = chamber_districts.filter(rothenberg_rating_id__in=rothenberg_class['values'])
                #district_list =  [i.id for i in districts]
                print "Handling rothenberg id = %s for chamber = %s" % (rothenberg_class['name'], chamber['name'])
                
                
                for district in districts:
                    district_result = {'district':district, 'results':[]}
                    #print "handling %s" % district
                    party_list = ['D', 'R']
                    if district.pk in independent_districts:
                        party_list.append("I")
                    #print district, rothenberg_class
                    candidates = all_candidates.filter(district=district).exclude(not_seeking_reelection=True)
                    for candidate in candidates:
                        if candidate.candidate_status in status_array:
                            pass
                            #print "losing candidate: %s candidate: %s - %s" % (district, candidate, candidate.show_candidate_status())
                        elif not candidate.party:
                            pass
                            #print "has a party %s candidate: %s party=%s- %s" % (district, candidate, candidate.party, candidate.show_candidate_status())
                        elif candidate.party in party_list:
                            #print "General contestant: %s, %s" % (candidate, candidate.party)
                            candidate.is_general_candidate = True
                            district_result['results'].append(candidate)
                    class_dict[rothenberg_class['name']]['results'].append(district_result)
                results_dict[chamber['name']].append(class_dict)

        print results_dict             
                            
