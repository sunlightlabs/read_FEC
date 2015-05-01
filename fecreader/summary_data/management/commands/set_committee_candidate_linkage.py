# Sets the curated_candidate_overlay field in committee_overlay from the Authorized_Candidate_Committees model. Use pop_auth_committees to set the data in Authorized_Candidate_Committees itself. 

from django.core.management.base import BaseCommand, CommandError

from summary_data.models import Authorized_Candidate_Committees, Candidate_Overlay, Committee_Overlay
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = ['2016']
    

class Command(BaseCommand):
    help = "Sets the curated_candidate_overlay field in committee_overlay from the Authorized_Candidate_Committees model"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        accs = Authorized_Candidate_Committees.objects.filter(cycle=CURRENT_CYCLE)
        for acc in accs:
            como = cando = None
            
            try:
                como = Committee_Overlay.objects.get(fec_id=acc.committee_id, cycle=CURRENT_CYCLE)
            except Committee_Overlay.DoesNotExist:
                print "Missing committee overlay for %s %s and cycle %s" % (acc.committee_name, acc.committee_id, CURRENT_CYCLE)
                continue
                
            try:
                cando = Candidate_Overlay.objects.get(fec_id=acc.candidate_id, cycle=CURRENT_CYCLE)
            except Candidate_Overlay.DoesNotExist:
                #print "Missing candidate overlay for candidate--committee name is:%s committee_id is: %s" % (acc.committee_name, acc.candidate_id)
                continue
            except Candidate_Overlay.MultipleObjectsReturned:
                print "Multiple candidate overlays returned for candidate--committee name is:%s committee_id is: %s during cycle %s" % (acc.committee_name, acc.candidate_id, CURRENT_CYCLE)
                
            como.curated_candidate = cando
            como.save()