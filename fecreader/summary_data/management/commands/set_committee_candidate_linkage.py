# Sets the curated_candidate_overlay field in committee_overlay from the Authorized_Candidate_Committees model. Use pop_auth_committees to set the data in Authorized_Candidate_Committees itself. 

from django.core.management.base import BaseCommand, CommandError

from summary_data.models import Authorized_Candidate_Committees, Candidate_Overlay, Committee_Overlay


class Command(BaseCommand):
    help = "Sets the curated_candidate_overlay field in committee_overlay from the Authorized_Candidate_Committees model"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        accs = Authorized_Candidate_Committees.objects.all()
        for acc in accs:
            como = cando = None
            
            try:
                como = Committee_Overlay.objects.get(fec_id=acc.committee_id)
            except Committee_Overlay.DoesNotExist:
                print "Missing committee overlay for %s %s" % (acc.committee_name, acc.committee_id)
                continue
                
            try:
                cando = Candidate_Overlay.objects.get(fec_id=acc.candidate_id)
            except Candidate_Overlay.DoesNotExist:
                print "Missing candidate overlay for candidate--committee name is:%s committee_id is: %s" % (acc.committee_name, acc.candidate_id)
                continue
                
            como.curated_candidate = cando
            como.save()