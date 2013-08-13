from django.core.management.base import BaseCommand, CommandError
from ftpdata.models import Candidate
from summary_data.models import Candidate_Overlay
from summary_data.utils.overlay_utils import make_candidate_overlay_from_masterfile


election_year = 2014
cycle = str(election_year)

class Command(BaseCommand):
    help = "Add new candidates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        candidates = Candidate.objects.filter(cycle=cycle, cand_election_year__in=[2013,2014])
        # We'll miss folks who put the wrong election year in their filing, but... 
        
        for candidate in candidates:
            # will doublecheck that it doesn't already exist before creating it
            make_candidate_overlay_from_masterfile(candidate.cand_id)
            
        
        