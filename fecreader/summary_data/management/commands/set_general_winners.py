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
        
        for chamber in chambers:
            chamber_candidates = all_candidates.filter(office=chamber['name'])
            chamber_districts = all_districts.filter(office=chamber['name'])
            

            for rothenberg_class in rothenberg_classes:
                districts = all_districts.filter(rothenberg_rating_id__in=rothenberg_class['values'])
                #district_list =  [i.id for i in districts]
                print "Handling rothenberg id = %s for chamber = %s" % (rothenberg_class['name'], chamber['name'])
                
                
                for district in districts:
                    print "handling %s" % district
                    party_list = ['D', 'R']
                    if district.pk in independent_districts:
                        party_list.append("I")
                    print district, rothenberg_class
                    candidates = all_candidates.filter(district=district).exclude(not_seeking_reelection=True)
                    for candidate in candidates:
                        if candidate.candidate_status in status_array:
                            pass
                            #print "losing candidate: %s candidate: %s - %s" % (district, candidate, candidate.show_candidate_status())
                        elif candidate.party:
                            pass
                            #print "has a party %s candidate: %s party=%s- %s" % (district, candidate, candidate.party, candidate.show_candidate_status())
                        if candidate.party in party_list:
                            print "General contestant: %s, %s" % (candidate, candidate.party)
                            candidate.is_general_candidate = True
                            # candidate.save()
                    for party in party_list:
                        party_candidates = candidates.filter(party=party).exclude(candidate_status__in=status_array)
                        if len(party_candidates) > 1:
                            print "More than 1 %s candidate in %s" % (party, district)
                    
                    if rothenberg_class['assigned_party']:
                        probable_winner = candidates.filter(party=rothenberg_class['assigned_party']).exclude(candidate_status__in=status_array)
                        if probable_winner:
                            if len(probable_winner) > 1:
                                print "** Warning--more than 1 %s probable winner in %s" % ( rothenberg_class['assigned_party'], district)
                            elif len(probable_winner) == 0:
                                print "Warning--No %s probable winner in %s" % ( rothenberg_class['assigned_party'], district)
                            elif len(probable_winner) == 1:
                                print "Setting winner %s %s in %s" % (probable_winner[0], rothenberg_class['assigned_party'], district)
                                candidate.cand_is_gen_winner = True
                                #candidate.save()
                    
                    # Get probable winner:
                        
                    
                
            #  Is this candidate a winner in the general election?
            # cand_is_gen_winner = models.NullBooleanField(null=True)

            #  Are they in the general election ? 
            # is_general_candidate = models.NullBooleanField(null=True)
"""

d = District.objects.filter(office='H')

rothenberg_rating_id, rothenberg_rating_text,

"""
            
            