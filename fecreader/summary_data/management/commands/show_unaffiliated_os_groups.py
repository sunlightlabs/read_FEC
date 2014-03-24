""" Show outside spending groups that haven't been assigned. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay, Committee_Overlay



class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # Leave out committees we've verified by hand
        committee_list = Committee_Overlay.objects.filter(total_indy_expenditures__gte=1000, political_orientation__isnull=True).order_by('-total_indy_expenditures')
        for committee in committee_list:
            print "%s total %s pro dem: %s pro rep: %s antidem %s antirep %s " % (committee.name, committee.total_indy_expenditures, committee.ie_support_dems, committee.ie_support_reps, committee.ie_oppose_dems, committee.ie_oppose_reps)