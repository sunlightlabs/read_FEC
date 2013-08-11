from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Max, Min


from formdata.models import Filing_Header, SkedA, SkedE, Committee_Changed
from fec_alerts.models import new_filing
from formdata.utils.fec_import_logging import fec_logger


# for debugging
from django.db import connection

# superceded operations are slow bc of query structure -- need to hit indexes here
def mark_superceded_F24s(new_f3x_filing_header):
    print "marking superceded F24 body rows"
    
    # we only mark the child rows as superceded--the filing itself isn't, because it's possible, in theory, that it's *half* superceded. 
    coverage_from_date = new_f3x_filing_header.coverage_from_date
    coverage_through_date = new_f3x_filing_header.coverage_through_date
    raw_filer_id = new_f3x_filing_header.raw_filer_id
    
    filing_numbers = Filing_Header.objects.filter(raw_filer_id=raw_filer_id).values('filing_number')
    filing_array = []
    for i in filing_numbers:
        filing_array.append(i['filing_number'])
    
    SkedE.objects.filter(form_type__istartswith='F24', filing_number__in=filing_array, superceded_by_amendment=False, expenditure_date_formatted__gte=coverage_from_date, expenditure_date_formatted__lte=coverage_from_date).update(superceded_by_amendment=True)
   
    
    ## This isn't necessary b/c the dirty flag will be set by the workers entering the new filing. 
    # mark the committee as being dirty;
    #Committee_Changed.objects.get_or_create(committee_id=raw_filer_id)
    
        
def mark_superceded_F65s(new_f3_filing_header):
    print "marking superceded F65s"
    
    coverage_from_date = new_f3_filing_header.coverage_from_date
    coverage_through_date = new_f3_filing_header.coverage_through_date
    raw_filer_id = new_f3_filing_header.raw_filer_id
    
    filing_numbers = Filing_Header.objects.filter(raw_filer_id=raw_filer_id).values('filing_number')
    filing_array = []
    for i in filing_numbers:
        filing_array.append(i['filing_number'])
    SkedA.objects.filter(form_type__istartswith='F65', filing_number__in=filing_array, superceded_by_amendment=False, contribution_date__gte=coverage_from_date, contribution_date__lte=coverage_from_date).update(superceded_by_amendment=True)
    
    #print connection.queries
    
    # mark the committee as being dirty;
    # Committee_Changed.objects.get_or_create(committee_id=raw_filer_id)
    
def summarize_f24(new_filing):
    filing_ies = SkedE.objects.filter(filing_number=new_filing.filing_number)
    
    results = filing_ies.aggregate(tot_spent=Sum('expenditure_amount'), start_date=Min('expenditure_date_formatted'), end_date=Max('expenditure_date_formatted'))
    if results:
        new_filing.tot_spent = results['tot_spent']
        new_filing.coverage_from_date = results['start_date']
        new_filing.coverage_to_date = results['end_date']
        new_filing.save()
    
def summarize_f6(new_filing):
    filing_skeda = SkedA.objects.filter(filing_number=new_filing.filing_number)

    results = filing_skeda.aggregate(tot_raised=Sum('contribution_amount'), start_date=Min('contribution_date_formatted'), end_date=Max('contribution_date_formatted'))
    if results:
        new_filing.tot_raised = results['tot_raised']
        new_filing.coverage_from_date = results['start_date']
        new_filing.coverage_to_date = results['end_date']
        new_filing.save()
    
    

class Command(BaseCommand):
    help = "Mark the body rows as being superceded as appropriate; also set the new_filing data for stuff that can only be calculated after body rows have run."
    requires_model_validation = False
    

    def handle(self, *args, **options):
        logger=fec_logger()
        
        filings_to_process = new_filing.objects.filter(previous_amendments_processed=True,header_is_processed=True, data_is_processed=True, body_rows_superceded=False).order_by('filing_number')
        for this_filing in filings_to_process:
            print "processing %s " % (this_filing.filing_number)
            
            
            # Create summary data for some forms that don't have it in the header. This script only runs after all the body rows of these filings have been entered; most other summary data is entered earlier in the process. 
            if this_filing.form_type.upper() in ['F24', 'F24A', 'F24N']:
                summarize_f24(this_filing)
            elif this_filing.form_type.upper() in ['F6', 'F6A', 'F6N']:
                summarize_f6(this_filing)
            
            # get the corresponding filing header
            this_filing_header = None
            try:
                this_filing_header = Filing_Header.objects.get(filing_number = this_filing.filing_number)
            except Filing_Header.DoesNotExist:
                # log this 
                msg = 'mark_superceded_body_rows: Couldn\'t find a filing header for # %s' % (this_filing.filing_number)
                logger.info(msg) 
                
            
            
            # if it's got sked E's and it's an F3X, overwrite 24 hr report
            if this_filing_header.form=='F3X':
                # need more logical tests--needs to be candidate pcc... 
                
                try:
                    this_filing_header.lines_present['SchE']
                    mark_superceded_F24s(this_filing_header)
                except KeyError:
                    pass


            # if it's a F3 remove F65's        
            if this_filing_header.form=='F3':
                try:
                    this_filing_header.lines_present['SchA']
                    mark_superceded_F65s(this_filing_header)
                except KeyError:
                    pass
            if this_filing_header.form=='F3':        
                mark_superceded_F65s(this_filing_header)
            this_filing.body_rows_superceded = True
            this_filing.save()
