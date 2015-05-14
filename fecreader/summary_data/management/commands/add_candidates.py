from django.core.management.base import BaseCommand, CommandError
from ftpdata.models import Candidate
from summary_data.models import Candidate_Overlay
from summary_data.utils.overlay_utils import make_candidate_overlay_from_masterfile
from django.conf import settings


try:
    ACTIVE_CYCLES = settings.ACTIVE_CYCLES
except:
    print "Missing active cycle list. Defaulting to 2016. "
    ACTIVE_CYCLES = ['2016']


ACTIVE_CYCLES = ['2016']

class Command(BaseCommand):
    help = "Add new candidates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        for cycle in ACTIVE_CYCLES:
        
            candidates = Candidate.objects.filter(cycle=cycle, cand_election_year__in=[int(cycle)-1,int(cycle)])
            # We'll miss folks who put the wrong election year in their filing, but... 
        
            for candidate in candidates:
                # will doublecheck that it doesn't already exist before creating it
                make_candidate_overlay_from_masterfile(candidate.cand_id, election_year=candidate.cand_election_year, cycle_to_copy_from=cycle, cycle_to_copy_to=cycle )
            
        
        