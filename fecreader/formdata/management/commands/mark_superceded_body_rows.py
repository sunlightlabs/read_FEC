from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Max, Min


from formdata.models import SkedA, SkedE
from fec_alerts.models import new_filing
from formdata.utils.fec_import_logging import fec_logger


# for debugging
from django.db import connection

# superceded operations are slow bc of query structure -- need to hit indexes here
def mark_superceded_F24s(new_f3x_new_filing):
    
    # we only mark the child rows as superceded--the filing itself isn't, because it's possible, in theory, that it's *half* superceded. 
    coverage_from_date = new_f3x_new_filing.coverage_from_date
    coverage_through_date = new_f3x_new_filing.coverage_to_date
    raw_filer_id = new_f3x_new_filing.fec_id
    
    filing_numbers = new_filing.objects.filter(fec_id=raw_filer_id, form_type__startswith='F24').values('filing_number')
    filing_array = []
    for i in filing_numbers:
        filing_array.append(i['filing_number'])
    
    updated = SkedE.objects.filter(filing_number__in=filing_array, superceded_by_amendment=False, expenditure_date_formatted__gte=coverage_from_date, expenditure_date_formatted__lte=coverage_through_date).update(superceded_by_amendment=True)
    if updated:
        print "marked %s superceded F24s" % updated
    
        
def mark_superceded_F65s(new_f3x_new_filing):
    
    coverage_from_date = new_f3x_new_filing.coverage_from_date
    coverage_through_date = new_f3x_new_filing.coverage_to_date
    raw_filer_id = new_f3x_new_filing.fec_id
    
    filing_numbers = new_filing.objects.filter(fec_id=raw_filer_id, form_type__startswith='F6').values('filing_number')
    filing_array = []
    for i in filing_numbers:
        filing_array.append(i['filing_number'])
    updated = SkedA.objects.filter(filing_number__in=filing_array, superceded_by_amendment=False, contribution_date__gte=coverage_from_date, contribution_date__lte=coverage_through_date).update(superceded_by_amendment=True)
    if updated:
        print "marked %s superceded F65s" % updated
        
    
def mark_superceded_F57s(new_monthly_f5):
    print "marking superceded F57s"
    
    coverage_from_date = new_monthly_f5.coverage_from_date
    coverage_through_date = new_monthly_f5.coverage_to_date
    raw_filer_id = new_monthly_f5.fec_id
    
    filing_numbers = new_filing.objects.filter(fec_id=raw_filer_id, is_f5_quarterly=False).values('filing_number')
    filing_array = []
    for i in filing_numbers:
        filing_array.append(i['filing_number'])
    updated = SkedE.objects.filter(form_type__istartswith='F57', filing_number__in=filing_array, superceded_by_amendment=False, expenditure_date_formatted__gte=coverage_from_date, expenditure_date_formatted__lte=coverage_through_date).update(superceded_by_amendment=True)
    if updated:
        print "marked %s superceded F57s" % updated
        
    
def summarize_f24(new_filing):
    filing_ies = SkedE.objects.filter(filing_number=new_filing.filing_number)
    
    results = filing_ies.aggregate(tot_spent=Sum('expenditure_amount'), start_date=Min('expenditure_date_formatted'), end_date=Max('expenditure_date_formatted'))
    if results:
        new_filing.tot_spent = results['tot_spent']
        new_filing.tot_ies = results['tot_spent']
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
    
def summarize_nonquarterly_f5(new_filing):
    filing_ies = SkedE.objects.filter(filing_number=new_filing.filing_number)
    
    results = filing_ies.aggregate(start_date=Min('expenditure_date_formatted'), end_date=Max('expenditure_date_formatted'))
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
            

            elif this_filing.form_type.startswith('F5') and not this_filing.is_f5_quarterly:
                summarize_nonquarterly_f5(this_filing)
                
            elif this_filing.form_type.startswith('F5') and this_filing.is_f5_quarterly:
                mark_superceded_F57s(this_filing)
            
            # if it's got sked E's and it's an F3X, overwrite 24 hr report
            elif this_filing.form_type.startswith('F3'):                
                try:
                    this_filing.lines_present['E']
                    mark_superceded_F24s(this_filing)
                except KeyError:
                    pass


                try:
                    this_filing.lines_present['A']
                    mark_superceded_F65s(this_filing)
                except KeyError:
                    pass
            
            # By now we should have dates for all filings, including the ones that don't start with a coverage from date
            # that we added by finding the first transaction date, so we can safely set the cycle. 
            if not this_filing.cycle:
                # we're about to save it, so don't hit the db twice.
                this_filing.set_cycle(save_now=False)
            
            this_filing.body_rows_superceded = True
            this_filing.save()
