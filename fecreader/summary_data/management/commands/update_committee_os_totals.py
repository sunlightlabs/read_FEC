""" Set PAC summary amounts. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Pac_Candidate, Candidate_Overlay, Committee_Overlay

cycle_start = date(2013,1,1)


class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # get all committees where there's outside spending
        committee_list = Pac_Candidate.objects.values('committee__fec_id').distinct()
        for ie_committee in committee_list:
            fec_id = ie_committee['committee__fec_id']
            
            total_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id).aggregate(total=Sum('total_ind_exp'))['total']
            dem_support_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='D',support_oppose__iexact='S' ).aggregate(total=Sum('total_ind_exp'))['total']
            rep_support_ies = dem_support_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='R',support_oppose__iexact='S' ).aggregate(total=Sum('total_ind_exp'))['total']
            dem_oppose_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='D',support_oppose__iexact='O' ).aggregate(total=Sum('total_ind_exp'))['total']
            rep_oppose_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='R',support_oppose__iexact='O' ).aggregate(total=Sum('total_ind_exp'))['total']
            
            print "total=%s support d = %s support r = %s oppose d = %s oppose r = %s" % (total_ies, dem_support_ies, rep_support_ies, dem_oppose_ies, rep_oppose_ies)
            
            try:
                this_committee = Committee_Overlay.objects.get(fec_id=fec_id)
            except:
                continue
                
            this_committee.total_indy_expenditures = total_ies
            this_committee.ie_support_dems = dem_support_ies
            this_committee.ie_support_reps = rep_support_ies
            this_committee.ie_oppose_dems = dem_oppose_ies
            this_committee.ie_oppose_reps = rep_oppose_ies
            
            this_committee.save()
            