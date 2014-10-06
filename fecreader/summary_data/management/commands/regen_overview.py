from datetime import datetime, date

from django.template import Template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.db.models import Sum
from django.core.management.base import BaseCommand, CommandError


from formdata.models import SkedE
from summary_data.models import Committee_Overlay

PROJECT_ROOT = settings.PROJECT_ROOT


CYCLE_START = date(2013,1,1)

class Command(BaseCommand):
    help = "Regenerate the main static overview page."
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        
        print "summaries"
        summary_obj = {}
        
        all_independent_expenditures = SkedE.objects.filter(superceded_by_amendment=False, expenditure_date_formatted__gte=CYCLE_START)
        summary_obj['ie_sum'] = all_independent_expenditures.aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
        print "positive vs negative"
        # postive vs negative
        summary_obj['positive'] = all_independent_expenditures.filter(support_oppose_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['negative'] = all_independent_expenditures.filter(support_oppose_checked='O').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']

        print "target party breakdown"
        # breakdown by target party
        summary_obj['pro_dem'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['pro_rep'] = all_independent_expenditures.filter(support_oppose_checked='S', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['anti_dem'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='D').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['anti_rep'] = all_independent_expenditures.filter(support_oppose_checked='O', candidate_party_checked='R').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        
        print "office breakdown"
        # breakdown by target party
        summary_obj['senate'] = all_independent_expenditures.filter(candidate_office_checked='S').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
        summary_obj['house'] = all_independent_expenditures.filter(candidate_office_checked='H').aggregate(total_expenditures=Sum('expenditure_amount'))['total_expenditures']
       
        
        all_outside_spenders = Committee_Overlay.nulls_last_objects.filter(total_indy_expenditures__gt=0)
        print "outside spending types"
        # breakdown by types:
        summary_obj['party_committees'] = all_outside_spenders.filter(ctype__in=('X', 'Y', 'Z')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        # includes hybrids
        summary_obj['super_pacs'] = all_outside_spenders.filter(ctype__in=('O', 'U', 'V', 'W')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        # non-committees:
        summary_obj['non_committees'] = all_outside_spenders.filter(ctype__in=('I')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        summary_obj['oth_committees'] = all_outside_spenders.filter(ctype__in=('N', 'Q')).aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        
        print "outside spending parties"
        # breakdown by parties 
        summary_obj['dem_affil'] = all_outside_spenders.filter(political_orientation='D').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        summary_obj['rep_affil'] = all_outside_spenders.filter(political_orientation='R').aggregate(total_expenditures=Sum('total_indy_expenditures'))['total_expenditures']
        
        update_time = datetime.now()
        c = Context({"update_time": update_time, "sums": summary_obj})
        this_template = get_template('generated_pages/overview_outside_money.html')
        result = this_template.render(c)
        template_path = PROJECT_ROOT + "/templates/generated_pages/overview_outside_money_include.html"
        output = open(template_path, 'w')
        output.write(result)
        output.close()