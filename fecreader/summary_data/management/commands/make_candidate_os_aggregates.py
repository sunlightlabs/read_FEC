""" Make outside spending aggregates w/r/t candidates """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Pac_Candidate, Candidate_Overlay

cycle_start = date(2013,1,1)


class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        candidate_ids = SkedE.objects.filter(superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_start).exclude(candidate_id_checked__isnull=True).values('candidate_id_checked').order_by('candidate_id_checked').distinct()
        for candidate_id in candidate_ids:
            print "handling %s" % (candidate_id['candidate_id_checked'])
            try:
                candidate = Candidate_Overlay.objects.get(fec_id=candidate_id['candidate_id_checked'])
                
                total_supporting = SkedE.objects.filter(expenditure_date_formatted__gte=cycle_start, superceded_by_amendment=False, candidate_checked=candidate, support_oppose_checked__iexact='S').aggregate(total=Sum('expenditure_amount'))
                total_opposing = SkedE.objects.filter(expenditure_date_formatted__gte=cycle_start, superceded_by_amendment=False, candidate_checked=candidate, support_oppose_checked__iexact='O').aggregate(total=Sum('expenditure_amount'))
                total = SkedE.objects.filter(expenditure_date_formatted__gte=cycle_start, superceded_by_amendment=False, candidate_checked=candidate).aggregate(total=Sum('expenditure_amount'))
                
                candidate.total_expenditures = total['total'] or 0
                candidate.expenditures_supporting = total_supporting['total'] or 0
                candidate.expenditures_opposing = total_opposing['total'] or 0
                candidate.save()
                
                
            except Candidate_Overlay.DoesNotExist:
                continue
            
            except Candidate_Overlay.MultipleObjectsReturned:
                print "Warning, multiple candidates found: %s" % (candidate_id['candidate_id_checked'])
                # should log this somewhere... 
                continue
            