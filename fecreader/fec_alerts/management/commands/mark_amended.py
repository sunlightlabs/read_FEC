from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from fec_alerts.models import new_filing



class Command(BaseCommand):
    help = "Mark the originals as being amended."
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        all_new_amendment_headers = new_filing.objects.filter(previous_amendments_processed=False,new_filing_details_set=True).order_by('filing_number')
        for new_amended_filing in all_new_amendment_headers:
            #print "processing %s " % (new_amended_filing.filing_number)

            this_filing_type = new_amended_filing.form_type.upper()
            # only run it if its a form we parse. 
            if new_amended_filing.is_amendment and not (this_filing_type in ['F1A', 'F2A', 'F1', 'F2']):
                filing_num = new_amended_filing.filing_number
                
                try:
                    original = new_filing.objects.get(filing_number=new_amended_filing.amends_filing)
                    #print "Writing amended original: %s %s" % (original.filing_number, header.filing_number)
                    original.is_superceded=True
                    original.amended_by = new_amended_filing.filing_number
                    original.save()
                except new_filing.DoesNotExist:
                    pass
            
    
                # Now find others that amend the same filing 
                earlier_amendments = new_filing.objects.filter(is_amendment=True,amends_filing=new_amended_filing.amends_filing, filing_number__lt=filing_num)
                for earlier_amendment in earlier_amendments:
                    #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
                    earlier_amendment.is_superceded=True
                    earlier_amendment.amended_by = filing_num
                    earlier_amendment.save()

            # mark that this has had it's amendments processed:
            new_amended_filing.previous_amendments_processed = True
            new_amended_filing.save()
