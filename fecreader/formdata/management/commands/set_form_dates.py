from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError

from formdata.models import Filing_Header


   


class Command(BaseCommand):
    help = "Set form dates from headers where we've got 'em. Assumes they are null initially"
    requires_model_validation = False

    def handle(self, *args, **options):
        
        all_headers = Filing_Header.objects.all().values('pk')
        for header_pk in all_headers:
            header = Filing_Header.objects.get(pk=header_pk['pk'])
            
            header_line = header.header_data
            from_date = None
            through_date = None
            try:
                if header_line['coverage_from_date']:
                    from_date = dateparse(header_line['coverage_from_date'])
                    through_date = dateparse(header_line['coverage_through_date'])
                    
                    header.coverage_from_date = from_date
                    header.coverage_through_date = through_date
                    header.save()
                    
            except KeyError:
                continue
            
        