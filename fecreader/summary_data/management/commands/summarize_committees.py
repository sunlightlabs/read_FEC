from summary_data.utils.summary_utils import summarize_committee_periodic

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Run committee summary routines"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        summarize_committee_periodic('C00532705')