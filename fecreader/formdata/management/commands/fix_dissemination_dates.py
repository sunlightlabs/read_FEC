


from django.core.management.base import BaseCommand, CommandError
from datetime import date
from fec_alerts.models import new_filing
from formdata.models import SkedE
from parsing.filing import filing
from parsing.form_parser import form_parser, ParserMissingError
from fec_alerts.utils.form_mappers import *

# see https://github.com/djangonauts/djorm-ext-hstore
# from djorm_hstore.expressions import HstoreExpression as HE




def fix_dissemination_date(this_filing, fp):
    ## we gotta parse the rows again. 
    
    print "handling %s" % this_filing.filing_number
    f1 = filing(this_filing.filing_number)
    form = f1.get_form_type()
    version = f1.get_version()
    filer_id = f1.get_filer_id()
    # This is being written when the current version is 8.1--the only version to include dissemination date.
    if not version == '8.1':
        return None
    
    linenum = 0
    
    # run through all the lines:
    while True:
        linenum += 1
        row = f1.get_body_row()
        if not row:
            break
        
        linedict = None
        try:
            linedict = fp.parse_form_line(row, version)
        except ParserMissingError:
            msg = 'process_filing_body: Unknown line type in filing %s line %s: type=%s Skipping.' % (this_filing.filing_number, linenum, row[0])
        
        # ignore everything but sked E's -- note that sked F57 *does not* have this issue.
        if linedict['form_parser'] == 'SchE':
            dissemination_date = linedict['dissemination_date']
            expenditure_date = linedict['expenditure_date']
            transaction_id = linedict['transaction_id']
            
            print "filingnum=%s dissemination_date=%s expenditure_date=%s transaction_id=%s" % (this_filing.filing_number, dissemination_date, expenditure_date, transaction_id)
            
            # then fix the original date in the db. 
        
    
    
    

class Command(BaseCommand):
    help = "Fix skede lines in fecfile v8.1 to use the dissemination date as the effective date, not the expenditure date. "
    
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # get all the fec filings with IEs in them:
        all_ie_filings = new_filing.objects.filter(tot_ies__gt=0, filed_date__gte=date(2014,1,14))
        fp = form_parser()
        for f in all_ie_filings:
            fix_dissemination_date(f, fp)
        