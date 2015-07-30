"""
try to attach missing lines
"""

from django.core.management.base import BaseCommand, CommandError

from process_skede_lines import attach_ie_target
from formdata.models import SkedE
from datetime import date


class Command(BaseCommand):
    help = "Set the name and details of the candidate targetted"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        skedes_to_process = SkedE.objects.filter(candidate_checked__isnull=True, effective_date__gte=date(2013,1,1))
        for skede_to_process in skedes_to_process:
            attach_ie_target(skede_to_process)