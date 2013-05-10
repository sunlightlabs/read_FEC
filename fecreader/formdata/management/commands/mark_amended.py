from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from formdata.models import Filing_Header
from fec_alerts.models import new_filing



class Command(BaseCommand):
    help = "Mark the originals as being amended."
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        all_new_amendment_headers = new_filing.objects.filter(previous_amendments_processed=False,header_is_processed=True).order_by('filing_number')
        for new_amended_filing in all_new_amendment_headers:
            print "processing %s " % (new_amended_filing.filing_number)
            
            this_filing_type = new_amended_filing.form_type.upper()
            # only run it if its a form we parse. 
            if this_filing_type.endswith('A') and not (this_filing_type in ['F1A', 'F2A']):
                filing_num = new_amended_filing.filing_number
                try:
                    header = Filing_Header.objects.get(filing_number=filing_num)
                except Filing_Header.DoesNotExist:
                    # probably it's another weird form type
                    print "***missing %s %s" % (filing_num, new_amended_filing.form_type)
                    continue
                try:
                    original = Filing_Header.objects.get(filing_number=header.amends_filing)
                    #print "Writing amended original: %s %s" % (original.filing_number, header.filing_number)
                    original.is_superceded=True
                    original.amended_by = header.filing_number
                    original.save()
                except Filing_Header.DoesNotExist:
                    pass
            
    
                # Now find others that amend the same filing 
                earlier_amendments = Filing_Header.objects.filter(is_amendment=True,amends_filing=header.amends_filing, filing_number__lt=header.filing_number)
                for earlier_amendment in earlier_amendments:
                    #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
                    earlier_amendment.is_superceded=True
                    earlier_amendment.amended_by = header.filing_number
                    earlier_amendment.save()

            # mark that this has had it's amendments processed:
            new_amended_filing.previous_amendments_processed = True
            new_amended_filing.save()
"""
                ## Now mark all filing rows
                all_amended_headers = Filing_Header.objects.filter(is_amended=True).order_by('filing_number')
                for header in all_amended_headers:
                    rows = Filing_Rows.objects.filter(parent_filing=header)
                    for row in rows:
                        row.superceded_by_amendment=True
                        row.save()
"""