from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from formdata.models import Filing_Header


class Command(BaseCommand):
    help = "Read header forms"
    requires_model_validation = False

    
    
    def handle(self, *args, **options):
        data_hash = {}
        all_headers = Filing_Header.objects.all()
        for a in all_headers:
            header = a.header_data
            form = a.form
            
            try:
                dateraw = header['coverage_from_date']
                date = dateparse(dateraw)
                dateraw = header['coverage_through_date']
                date = dateparse(dateraw)
            except KeyError:
                print "Missing!!! %s" % form
                            
                try:
                    num_found = data_hash[form]
                    num_found += 1
                    data_hash[form] = num_found
                except KeyError:
                    data_hash[form] = 1
            
        print data_hash