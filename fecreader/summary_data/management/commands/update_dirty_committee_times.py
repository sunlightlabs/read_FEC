from datetime import date

from django.core.management.base import BaseCommand, CommandError

from summary_data.utils.summary_utils import update_committee_times
from summary_data.models import Committee_Overlay
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'
    
class Command(BaseCommand):
    help = "Redo the summaries of *all committees* - not just those that need it"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_committees = Committee_Overlay.objects.filter(is_dirty=True, cycle=CURRENT_CYCLE)
        for committee in all_committees:
            update_committee_times(committee, CURRENT_CYCLE)
            committee.is_dirty=False
            committee.save()


