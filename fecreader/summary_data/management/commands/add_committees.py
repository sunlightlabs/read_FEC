""" Create new committees from the FEC's masterfile. If a committee already exists, it will be updated with current information. """

from django.core.management.base import BaseCommand, CommandError
from ftpdata.models import Committee
from summary_data.models import Committee_Overlay
from summary_data.utils.overlay_utils import make_committee_overlay_from_masterfile
from django.conf import settings


try:
    ACTIVE_CYCLES = settings.ACTIVE_CYCLES
except:
    print "Missing active cycle list. Defaulting to 2016. "
    ACTIVE_CYCLES = ['2016']


class Command(BaseCommand):
    help = "Add new candidates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        for cycle in ACTIVE_CYCLES:
        
            committees = Committee.objects.filter(cycle=int(cycle))
            # We'll miss folks who put the wrong election year in their filing, but... 
        
            for committee in committees:
                # will doublecheck that it doesn't already exist before creating it
                make_committee_overlay_from_masterfile(committee.cmte_id, cycle_to_copy_from=int(cycle), cycle_to_copy_to=int(cycle))
            
        
        