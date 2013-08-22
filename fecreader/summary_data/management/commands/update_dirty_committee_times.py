from datetime import date

from django.core.management.base import BaseCommand, CommandError



from summary_data.utils.summary_utils import update_committee_times
from summary_data.models import Committee_Overlay


class Command(BaseCommand):
    help = "Redo the summaries of *all committees* - not just those that need it"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_committees = Committee_Overlay.objects.filter(is_dirty=True)
        for committee in all_committees:
            update_committee_times(committee)
            committee.is_dirty=False
            committee.save()

