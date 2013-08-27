from django.core.management.base import BaseCommand, CommandError

from summary_data.utils.summary_utils import update_district_totals
from summary_data.models import District

class Command(BaseCommand):
    help = "Redo the summaries of *all districts*"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_districts = District.objects.all()
        for district in all_districts:
            update_district_totals(district)

