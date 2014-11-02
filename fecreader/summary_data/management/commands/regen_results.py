
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
        all_districts = District.objects.all()
        
        results = []
        
        for chamber in chambers:
            chamber_candidates = all_candidates.filter(office=chamber['name'])
            chamber_districts = all_districts.filter(office=chamber['value'])
            chamber_results = {'chamber':chamber['name'], 'rothenberg_classes':[]}
            
            if chamber['value'] == 'S':
                # there are 3 class 3 special elections here too, I believe: SC (graham's seat); hawaii, oklahoma
                chamber_districts = chamber_districts.filter(Q(term_class=2)|Q(id__in=[1003, 1053]))
                
            #results_dict[chamber['name']] = []

            for rothenberg_class in rothenberg_classes:
                rothenberg_class_dict = {'class':rothenberg_class['name'], 'id':rothenberg_class['id'],  'display':rothenberg_class['display'], 'districts':[]}
                
                districts = chamber_districts.filter(rothenberg_rating_id__in=rothenberg_class['values'])
                #district_list =  [i.id for i in districts]
                print "Handling rothenberg id = %s for chamber = %s" % (rothenberg_class['name'], chamber['name'])
                
                
                num_seats_in_class = len(districts)
                victors = {'D':0, 'R':0, 'I':0}
                
                for district in districts:
                    district_result = {'district':district, 'results':[]}
                    #print "handling %s" % district
                    party_list = ['D', 'R']
                    if district.pk in independent_districts:
                        party_list.append("I")
                    #print district, rothenberg_class
                    
                    ## just add 'is_general_candidate=True' here to filter once we've set this stuff. 
                    # candidates = all_candidates.filter(district=district).exclude(not_seeking_reelection=True)
                    candidates = all_candidates.filter(district=district, is_general_candidate=True).exclude(not_seeking_reelection=True)
                    
                    candidate_winners = 0
                    for candidate in candidates:
                        
                        if not candidate.party:
                            pass
                            
                        elif candidate.party in party_list:
                            district_result['results'].append(candidate)
                        
                        if candidate.cand_is_gen_winner:
                            
                            victors[candidate.party] = victors[candidate.party] + 1
                            candidate_winners += 1
                            if candidate_winners > 1:
                                print "***** MORE THAN ONE WINNING CANDIDATE FOUND **** %s" % (district)
                            
                    rothenberg_class_dict['districts'].append(district_result)
                    
                
                
                reformatted_victors = ['Democrats: '+str(victors['D']), 'Republicans: '+str(victors['R']),'Independents: '+str(victors['I'])]
                rothenberg_class_dict['victors'] = reformatted_victors 
                rothenberg_class_dict['num_seats']= num_seats_in_class
                # add stats about this class of districts
                chamber_results['rothenberg_classes'].append(rothenberg_class_dict)
            results.append({'chamber':chamber['name'] , 'results':chamber_results})
            

        print results             
                            
                            
        c = Context({"update_time": update_time, "results":results})
        this_template = get_template('generated_pages/overview_results.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_results_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()
