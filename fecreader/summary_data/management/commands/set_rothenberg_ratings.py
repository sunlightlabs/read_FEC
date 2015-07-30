# sets the rothenberg ratings from the rothenberg model; doesn't hit them externally.

from django.core.management.base import BaseCommand, CommandError

from rothenberg.models import HouseRace, SenateRace
from summary_data.models import District
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'




class Command(BaseCommand):
    help = "set rothenberg ratings from internal app--run after they've been reset"
    requires_model_validation = False

    def handle(self, *args, **options):
        districts = District.objects.filter(cycle=CURRENT_CYCLE)
        
        for district in districts:
            
            state = district.state
            office = district.office
            
            # Ignore non-state districts
            if state in ["AS", "DC", "GU", "MP", "PR", "VI"]:
                continue
            
            #print "Handling state=%s office=%s" % (state, office)
            if office=='H':
                office_district = district.office_district
                rothenberg_district = 1
                if office_district != '00':
                    rothenberg_district = int(office_district)
                try:
                    rating = HouseRace.objects.get(state=state, district=rothenberg_district, cycle=CURRENT_CYCLE)
                    #print "Got rating %s %s %s" % (rating.rating_id, rating.rating_label, rating.update_time)
                    district.rothenberg_rating_id = rating.rating_id
                    district.rothenberg_rating_text = rating.rating_label
                    district.rothenberg_update_time = rating.update_time
                    district.save()
                except HouseRace.DoesNotExist:
                    print "Missing %s %s" % (state, rothenberg_district)
                    
            elif office=='S':
                seat_class = district.term_class
                rothenberg_seat_class = 'I'
                if seat_class != 1:
                    if seat_class == 2:
                        rothenberg_seat_class = 'II'
                    elif seat_class == 3:
                        rothenberg_seat_class = 'III'
                
                try:
                    rating = SenateRace.objects.get(state=state, seat_class=rothenberg_seat_class, cycle=CURRENT_CYCLE)
                    #print "Got rating %s %s %s" % (rating.rating_id, rating.rating_label, rating.update_time)
                    district.rothenberg_rating_id = rating.rating_id
                    district.rothenberg_rating_text = rating.rating_label
                    district.rothenberg_update_time = rating.update_time
                    district.save()
                    
                except SenateRace.DoesNotExist:
                    print "Missing %s %s" % (state, rothenberg_seat_class)
                    
            
            elif office=='P':
                continue
                
            else:
                print "Missing chamber!!"


        