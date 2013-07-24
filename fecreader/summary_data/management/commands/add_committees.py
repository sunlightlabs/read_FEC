from django.core.management.base import BaseCommand, CommandError
from ftpdata.models import Committee
from summary_data.models import Committee_Overlay
from summary_data.utils.overlay_utils import make_committee_overlay_from_masterfile


election_year = 2014
cycle = str(election_year)

class Command(BaseCommand):
    help = "Add new candidates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        committees = Committee.objects.filter(cycle=cycle)
        # We'll miss folks who put the wrong election year in their filing, but... 
        
        for committee in committees:
            # will doublecheck that it doesn't already exist before creating it
            make_committee_overlay_from_masterfile(committee.cmte_id)
            
        
        