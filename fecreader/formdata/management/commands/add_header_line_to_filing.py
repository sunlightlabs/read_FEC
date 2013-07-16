# Requires the date is specified in filerange.py -- so we give the header a filed date. 

from os import system, path

from dateutil.parser import parse as dateparse
from datetime import date, timedelta, datetime

from django.core.management.base import BaseCommand, CommandError

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY

from formdata.models import Filing_Header
from formdata.utils.filing_processors import process_filing_header

from parsing.filerange import filerange



# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Add the header lines, which got munged up previously"
    requires_model_validation = False

    def handle(self, *args, **options):
        all_filings = Filing_Header.objects.all()
        for this_filing in all_filings:
            filing_number = this_filing.filing_number
            print "Processing %s" % filing_number
            f1 = filing(filing_number)
            form = f1.get_form_type()
            version = f1.get_version()

            # only parse forms that we're set up to read

            if not fp.is_allowed_form(form):
                if verbose:
                    print "Not a parseable form: %s - %s" % (form, filingnum)

                continue

            header = f1.get_first_row()
            header_line = fp.parse_form_line(header, version)
            this_filing.header_data=header_line
            this_filing.save()