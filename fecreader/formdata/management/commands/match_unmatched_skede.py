"""
try to attach missing lines
"""

from django.core.management.base import BaseCommand, CommandError

from process_skede_lines import attach_ie_target
from formdata.models import SkedE



class Command(BaseCommand):
    help = "Set the name and details of the candidate targetted"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        skedes_to_process = SkedE.objects.filter(candidate_checked__isnull=True)
        for skede_to_process in skedes_to_process:
            attach_ie_target(skede_to_process)