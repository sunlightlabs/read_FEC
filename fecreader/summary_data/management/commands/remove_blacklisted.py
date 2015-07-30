# Remove problematic entities.

from django.core.management.base import BaseCommand, CommandError


from summary_data.models import Committee_Overlay, Candidate_Overlay, Committee_Time_Summary, Authorized_Candidate_Committees
from fec_alerts.models import WebK, new_filing

blacklisted_committees = ['C00507947', 'C00428599']
blacklisted_candidates = ['P20003851', 'P80003205']

class Command(BaseCommand):
    help = "Set "
    requires_model_validation = False
    
    def handle(self, *args, **options):
        for fecid in blacklisted_committees:
            Committee_Overlay.objects.filter(fec_id=fecid).delete()
            Committee_Time_Summary.objects.filter(com_id=fecid).delete()
            Authorized_Candidate_Committees.objects.filter(committee_id=fecid).delete()
            WebK.objects.filter(com_id=fecid).delete()
            new_filing.objects.filter(fec_id=fecid).delete()
        
        for fecid in blacklisted_candidates:
            Candidate_Overlay.objects.filter(fec_id=fecid).delete()
            Authorized_Candidate_Committees.objects.filter(candidate_id=fecid).delete()
            