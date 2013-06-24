from django.core.management.base import BaseCommand, CommandError
from celeryproj.tasks import process_filing_body_celery
from fec_alerts.models import new_filing

from formdata.utils.fec_import_logging import fec_logger

class Command(BaseCommand):
    help = "Queue filing body row entry for execution by celery processes"
    requires_model_validation = False
    def handle(self, *args, **options):
        logger=fec_logger()
        filings_to_queue = new_filing.objects.filter(filing_is_downloaded=True, header_is_processed=True, data_is_processed=False, previous_amendments_processed=True).order_by('filing_number')
        for filing in filings_to_queue:
            msg = "send_body_row_jobs: Adding filing %s to entry queue" % (filing.filing_number)
            # print msg
            logger.info(msg)
            process_filing_body_celery.apply_async([filing.filing_number], queue='slow',routing_key="slow")
            
