from django.core.management.base import BaseCommand, CommandError

from formdata.models import SkedE
from summary_data.models import Committee_Overlay
from shared_utils.cycle_utils import get_cycle_from_date



def attach_committee_to_skedeline(skedeline):
    cycle_date = skedeline.effective_date
    THIS_CYCLE = None
    if cycle_date:
        THIS_CYCLE = get_cycle_from_date(cycle_date)
        
    try:
        co = Committee_Overlay.objects.get(fec_id=skedeline.filer_committee_id_number, cycle=THIS_CYCLE)
        skedeline.committee_name = co.name
        skedeline.committee_slug = co.slug
        skedeline.save()
        
    except Committee_Overlay.DoesNotExist:
        print "Missing committee overlay for %s and cycle %s" % (skedeline.filer_committee_id_number, THIS_CYCLE)
        
class Command(BaseCommand):
    help = "Set the name and details of the committee making the ie"
    requires_model_validation = False
    

    def handle(self, *args, **options):
        skedelines = SkedE.objects.filter(committee_name__isnull=True).order_by('filing_number')
        for this_line in skedelines:
            attach_committee_to_skedeline(this_line)
