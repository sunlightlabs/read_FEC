from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.models import Filing_Header

from formdata.utils.form_mappers import *


# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Count the number of lines present in each filing, and store it."
    requires_model_validation = False
    

    def handle(self, *args, **options):
        
        # just get the ids--otherwise django will load every column into memory
        # filter(form='F13')
        all_headers = Filing_Header.objects.all().order_by('filing_number').values('pk')[:2000]
        for header_pk in all_headers:
            pk = header_pk['pk']
            header = Filing_Header.objects.get(pk=pk)
            filingnum = header.filing_number
            f1 = filing(filingnum, read_from_cache=True, write_to_cache=True)
            f1.download()
            form = header.form
            version = header.version
            
            print "processing filingnum %s, form %s version %s" % (filingnum, form, version)
            
            line_dict = {}
            content_rows = f1.get_body_rows()
            total_lines = 0
            for row in content_rows:
                # instead of parsing the line, just assume form type is the first arg.
                r_type = row[0].upper().strip()
                
                # sometimes there are blank lines within files--see 707076.fec
                if not r_type:
                    continue
                    
                total_lines += 1
                # what type of line parser would be used here? 
                lp = fp.get_line_parser(r_type)
                if lp:
                    form = lp.form
                    r_type = form
                else:
                    print "Missing parser from %s" % (r_type) 
                
                try: 
                    num = line_dict[r_type]
                    line_dict[r_type] = num + 1
                except KeyError:
                    line_dict[r_type] = 1
            
            print "Found total lines = %s with dict=%s" % (total_lines, line_dict)
            #header.lines_present = line_dict
            #header.save()
            
            