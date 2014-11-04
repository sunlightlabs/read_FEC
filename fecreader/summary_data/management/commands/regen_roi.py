# rebuild roi file

from datetime import date, datetime
from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay, Pac_Candidate, Committee_Overlay, roi_pair


cycle_start = date(2013,1,1)
PROJECT_ROOT = settings.PROJECT_ROOT



class Command(BaseCommand):
    help = "Write ROI files"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        today = date.today()
        update_time = datetime.now()
        
        outside_spenders = Committee_Overlay.objects.filter(total_indy_expenditures__gt=0).order_by('-total_indy_expenditures')[:20]
        
        for os in outside_spenders:
            # ATTACH LINE ITEMS;
            ge_spending = roi_pair.objects.filter(committee=os, total_ind_exp__gte=50000).select_related('candidate').order_by('-total_ind_exp')
            os.ge = ge_spending
        
        c = Context({"update_time": update_time, "outside_spenders":outside_spenders})
        this_template = get_template('generated_pages/roi.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/roi_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()

