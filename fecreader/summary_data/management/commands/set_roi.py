""" Set roi data--which is really candidate-pac spending in the general election only. Need to erase entire model to get rid of bogus entries. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay, Pac_Candidate, Committee_Overlay, roi_pair

cycle_start = date(2013,1,1)


class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        run_summary = True
        
        if run_summary:
            # all skede general 2014 expenditures that are not superseded by an amendment
            summary = SkedE.objects.filter(election_code__in=['G2014', 'g2014']).exclude(superceded_by_amendment=True).exclude(candidate_checked__isnull=True).exclude(support_oppose_checked__isnull=True).exclude(expenditure_date_formatted__lt=cycle_start).order_by('candidate_checked', 'support_oppose_checked','filer_committee_id_number').values('candidate_checked', 'support_oppose_checked','filer_committee_id_number').annotate(total=Sum('expenditure_amount'))
        
            for summary_line in summary:
                print "Candidate: %s s/o: %s amt: %s committee_id %s " % (summary_line['candidate_checked'], summary_line['support_oppose_checked'], summary_line['total'], summary_line['filer_committee_id_number'])
                try:
                    committee = Committee_Overlay.objects.get(fec_id=summary_line['filer_committee_id_number'])
                    candidate = Candidate_Overlay.objects.get(pk=summary_line['candidate_checked'])
                    roi, created = roi_pair.objects.get_or_create(candidate=candidate, committee=committee, support_oppose=summary_line['support_oppose_checked'])
                    roi.total_ind_exp = int(round(summary_line['total']))
                    roi.save()
                except Committee_Overlay.DoesNotExist:
                    print "Missing committee overlay for %s" % (summary_line['filer_committee_id_number'])
        
        
        ## now that the individual roi pieces are set, aggregate them back to the committee.
        
        committee_list = roi_pair.objects.values('committee__fec_id').order_by('committee__fec_id').distinct()
        for ie_committee in committee_list:
            fec_id = ie_committee['committee__fec_id']
            committee = Committee_Overlay.objects.get(fec_id=fec_id)
            
            
            committee.support_winners = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner=True,support_oppose__iexact='S' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            committee.oppose_winners = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner=True,support_oppose__iexact='O' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            
            committee.support_losers = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner=False,support_oppose__iexact='S' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            committee.oppose_losers = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner=False,support_oppose__iexact='O' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            
            committee.support_unclassified = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner__isnull=True,support_oppose__iexact='S' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            committee.oppose_unclassified = roi_pair.objects.filter(committee__fec_id=fec_id, candidate__cand_is_gen_winner__isnull=True,support_oppose__iexact='O' ).aggregate(total=Sum('total_ind_exp'))['total'] or 0
            
            if ((committee.support_winners + committee.oppose_losers + committee.support_losers + committee.oppose_winners ) > 0):
                committee.roi = (committee.support_winners + committee.oppose_losers) / (committee.support_winners + committee.oppose_losers + committee.support_losers + committee.oppose_winners )
            else:
                committee.roi = None
            
            committee.save()
           
        
        
