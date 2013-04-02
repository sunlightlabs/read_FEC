from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from formdata.models import Filing_Header


class Command(BaseCommand):
    help = "Mark the originals as being amended."
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        # just get the ids--otherwise django will load every column into memory
        all_amendment_headers = Filing_Header.objects.filter(is_amendment=True).order_by('filing_number').values('pk')
        for header_pk in all_amendment_headers:
            pk = header_pk['pk']
            header = Filing_Header.objects.get(pk=pk)
            # First set the original:
            print "processing %s " % (header.filing_number)
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

"""
                ## Now mark all filing rows
                all_amended_headers = Filing_Header.objects.filter(is_amended=True).order_by('filing_number')
                for header in all_amended_headers:
                    rows = Filing_Rows.objects.filter(parent_filing=header)
                    for row in rows:
                        row.superceded_by_amendment=True
                        row.save()
"""