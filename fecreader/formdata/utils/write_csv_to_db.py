import csv, datetime
from cStringIO import StringIO

from formdata.models import *

# csv.DictWriter(csvfile, fieldnames, restval='', extrasaction='raise', dialect='excel', *args, **kwds)

class CSV_dumper(object):
    """ Helper class to aggregate csv data, which can then be loaded w/ raw postgres copy in a single transaction block. """
    
    def __init__(self):
        # do we want to use the filing number to leave breadcrumbs ? Probably not, but...
        
        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y%m%d_%H%M")
        
        self.fields = {}
        self.fields['A'] = sorted(SkedA._meta.get_all_field_names())
        self.fields['B'] = sorted(SkedB._meta.get_all_field_names())
        self.fields['E'] = sorted(SkedE._meta.get_all_field_names())
        
        self.writers = {}
        
        for sked in ['A', 'B', 'E']:
            self.writers[sked] = {}
            self.writers[sked]['stringio'] = StringIO()
            self.writers[sked]['writer'] = csv.DictWriter(self.writers[sked]['stringio'], self.fields[sked], restval='', extrasaction='ignore', lineterminator='\n')
    

    def getwriter(self, sked):
        return self.writers[sked.upper()]['writer']
    
    def writerow(self, sked, row):
        thiswriter = self.writers[sked]['writer']
        thiswriter.writerow(row)
        return 1
    
    def get_rowdata(self, sked):
        return self.writers[sked]['stringio'].getvalue()

    
"""         
from formdata.utils.write_csv_to_db import CSV_dumper
d = CSV_dumper()

data = {'filing_number':23}
d.writerow('E', data)
d.get_rowdata('E')
"""
    