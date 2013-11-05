from django.core.management.base import BaseCommand, CommandError

from formdata.models import SkedE
from summary_data.models import Committee_Overlay


def attach_committee_to_skedeline(skedeline):
    try:
        co = Committee_Overlay.objects.get(fec_id=skedeline.filer_committee_id_number)
        skedeline.committee_name = co.name
        skedeline.committee_slug = co.slug
        skedeline.save()
        
    except Committee_Overlay.DoesNotExist:
        print "Missing committee overlay for %s" % (skedeline.filer_committee_id_number)
        
class Command(BaseCommand):
    help = "Set the name and details of the committee making the ie"
    requires_model_validation = False
    

    def handle(self, *args, **options):
        skedelines = SkedE.objects.filter(committee_slug__isnull=True).order_by('filing_number')
        for this_line in skedelines:
            attach_committee_to_skedeline(this_line)
