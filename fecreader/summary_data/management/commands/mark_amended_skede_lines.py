"""
management command that makes sure all superceded sked e filings are listed as superceded in the body rows.
"""

from django.core.management.base import BaseCommand, CommandError
from formdata.models import Filing_Header, SkedE
from django.db import connection

class Command(BaseCommand):
    help = "Make sure sked e aggregates are set. Mostly redundant"
    requires_model_validation = False


    def handle(self, *args, **options):
        all_amended_filings = Filing_Header.objects.filter(is_superceded=True)
        for af in all_amended_filings:
            if af.lines_present:
                numlines = int(af.lines_present.get('E'))
                if numlines > 0:
                    print "updating %s - numrows = %s" % (af.filing_number, numlines)
                    SkedE.objects.filter(filing_number=af.filing_number).update(superceded_by_amendment=False)
                    print connection.queries[-1:]