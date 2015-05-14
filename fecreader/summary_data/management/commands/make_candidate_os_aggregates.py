""" Make outside spending aggregates w/r/t candidates """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Pac_Candidate, Candidate_Overlay
from shared_utils.cycle_utils import cycle_calendar
from django.conf import settings


try:
    ACTIVE_CYCLES = settings.ACTIVE_CYCLES
except:
    print "Missing current cycle list. Defaulting to 2016. "
    ACTIVE_CYCLES = ['2016']
    


class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False

    def handle(self, *args, **options):
        for cycle in ACTIVE_CYCLES:
            this_cycle_calendar = cycle_calendar[int(cycle)]
            this_cycle_start = this_cycle_calendar['start']
            this_cycle_end = this_cycle_calendar['end']
            
            candidate_ids = SkedE.objects.filter(superceded_by_amendment=False, expenditure_date_formatted__gte=this_cycle_start,expenditure_date_formatted__lte=this_cycle_end ).exclude(candidate_id_checked__isnull=True).values('candidate_id_checked').order_by('candidate_id_checked').distinct()
            for candidate_id in candidate_ids:
                print "handling candidate id %s" % (candidate_id['candidate_id_checked'])
                try:
                    candidate = Candidate_Overlay.objects.get(fec_id=candidate_id['candidate_id_checked'], cycle=cycle)
                
                    total_supporting = SkedE.objects.filter(expenditure_date_formatted__gte=this_cycle_start,expenditure_date_formatted__lte=this_cycle_end, superceded_by_amendment=False, candidate_checked=candidate, support_oppose_checked__iexact='S').aggregate(total=Sum('expenditure_amount'))
                    total_opposing = SkedE.objects.filter(expenditure_date_formatted__gte=this_cycle_start,expenditure_date_formatted__lte=this_cycle_end, superceded_by_amendment=False, candidate_checked=candidate, support_oppose_checked__iexact='O').aggregate(total=Sum('expenditure_amount'))
                    total = SkedE.objects.filter(expenditure_date_formatted__gte=this_cycle_start,expenditure_date_formatted__lte=this_cycle_end, superceded_by_amendment=False, candidate_checked=candidate).aggregate(total=Sum('expenditure_amount'))
                
                    candidate.total_expenditures = total['total'] or 0
                    candidate.expenditures_supporting = total_supporting['total'] or 0
                    candidate.expenditures_opposing = total_opposing['total'] or 0
                    candidate.save()
                
                
                except Candidate_Overlay.DoesNotExist:
                    print "Candidate overlay doesn't exist for candidate: %s" % (candidate_id['candidate_id_checked'])
                    continue
            
                except Candidate_Overlay.MultipleObjectsReturned:
                    print "Warning, multiple candidates found: %s" % (candidate_id['candidate_id_checked'])
                    # should log this somewhere... 
                    continue
            