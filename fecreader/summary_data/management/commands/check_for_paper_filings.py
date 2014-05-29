# Look for paper filings in electronic filers. Takes obnoxiously long to run. Should be run occasionally though. 

from django.core.management.base import BaseCommand, CommandError


from summary_data.models import Committee_Overlay
from summary_data.utils.summary_utils import summarize_committee_periodic_webk, update_committee_times


class Command(BaseCommand):
    help = "Set "
    requires_model_validation = False
    
    def handle(self, *args, **options):
        electronic_filers = Committee_Overlay.objects.filter(is_paper_filer=False)
        for thiscommittee in electronic_filers:
         summarize_committee_periodic_webk(thiscommittee.fec_id)
         update_committee_times(thiscommittee)
