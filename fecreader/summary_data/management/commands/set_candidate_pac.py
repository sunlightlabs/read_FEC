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
        summary = SkedE.objects.all().exclude(superceded_by_amendment=True).exclude(candidate_checked__isnull=True).exclude(support_oppose_checked__isnull=True).exclude(expenditure_date_formatted__lt=cycle_start).values('candidate_checked', 'support_oppose_checked','filer_committee_id_number').annotate(total=Sum('expenditure_amount'))
        for summary_line in summary:
            print "Candidate: %s s/o: %s amt: %s committee_id %s" % (summary_line['candidate_checked'], summary_line['support_oppose_checked'], summary_line['total'], summary_line['filer_committee_id_number'])
            pc, created = Pac_Candidate.objects.get_or_create(candidate__pk=summary_line['candidate_checked'], committee__fec_id=summary_line['filer_committee_id_number'], support_oppose=summary_line['support_oppose_checked'])
            pc.total_ind_exp = int(round(summary_line['expenditure_amount']))
            pc.save()
        