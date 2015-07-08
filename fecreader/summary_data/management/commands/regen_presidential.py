## godawful mess to redo some static pages. Best if this process doesn't live too long. 

import csv
from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Sum, Count
from django.core.management.base import BaseCommand, CommandError


#infile = open('shared_utils/2016ers_may.csv', 'r')
infile = open('shared_utils/2016ers_april_new.csv', 'r')

reader = csv.DictReader(infile)


PROJECT_ROOT = settings.PROJECT_ROOT


CYCLE_START = date(2013,1,1)

class Command(BaseCommand):
    help = "Regenerate the main static overview page."
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
        update_time = datetime.now()
        
        print "summaries"
        summary_obj_list = []
        
        for row in reader:
            #print row
            this_candidate = {}
            this_candidate['name'] = row['candidate']
            this_candidate['first_name'] = row['candidate_first']
            this_candidate['party'] = row['party'].upper()
            this_candidate['candidate_committees'] = []
            this_candidate['leadership_committees'] = []
            this_candidate['superpacs'] = []
            this_candidate['other_committees'] = []

                
            if row['prez_id']:
                this_candidate['candidate_committees'].append({'pac_name': row['prez_cmte'], 'pac_id':row['prez_id']})
        
            if row['pac_id']:
                this_candidate['leadership_committees'].append({'pac_name': row['leadership_pac'], 'pac_id':row['pac_id']})


            if row['other']:
                this_candidate['other_committees'].append({'pac_name': row['other'],'other_url': row['other_url'] })
            
            
            print this_candidate
        
            for sp_id in ("_1", "_2", "_3", "_4", "_5", "_6"):
                this_pac = row["super_pac" + sp_id]
                this_id = row["super_id" + sp_id]
            
                if this_id:
                    this_candidate['superpacs'].append({'pac_name': this_pac, 'pac_id':this_id})
            
        
            summary_obj_list.append(this_candidate)

        ## get sum summary data
        
        
        
        ## write out the template
                
        c = Context({"update_time": update_time, "summary_obj_list": summary_obj_list})
        this_template = get_template('generated_pages/presidential_april_2015.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/presidential_april_2015_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()
        
        ## deal with the inside spending
        