from datetime import date

from django.core.management.base import BaseCommand, CommandError



from summary_data.utils.summary_utils import update_committee_times
from summary_data.models import Committee_Overlay, Committee_Time_Summary

class Command(BaseCommand):
    help = "Set the names of committee time summaries that are missing them"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        ctss = Committee_Time_Summary.objects.filter(com_name__isnull=True)
        #all_committees = Committee_Overlay.objects.filter(ctype='I')
        for cts in ctss:
            print "trying %s" % cts.com_id
            try:
                co = Committee_Overlay.objects.get(fec_id=cts.com_id)
                cts.com_name = co.name
                cts.save()
            except Committee_Overlay.DoesNotExist:
                print "Missing committee %s" % (cts.com_id)
