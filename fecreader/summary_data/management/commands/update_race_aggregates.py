from django.core.management.base import BaseCommand, CommandError

from summary_data.utils.summary_utils import update_district_totals
from summary_data.models import District
from django.conf import settings


try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'
    

class Command(BaseCommand):
    help = "Redo the summaries of *all districts*"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        all_districts = District.objects.filter(cycle=CURRENT_CYCLE)
        for district in all_districts:
            update_district_totals(district)

