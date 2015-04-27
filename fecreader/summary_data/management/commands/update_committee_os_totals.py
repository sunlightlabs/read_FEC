""" Set PAC summary amounts. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.conf import settings


from formdata.models import SkedE
from summary_data.models import Pac_Candidate, Candidate_Overlay, Committee_Overlay
from shared_utils.cycle_utils import cycle_calendar


try:
    ACTIVE_CYCLES = settings.ACTIVE_CYCLES
except:
    print "Missing active cycle list. Defaulting to 2016. "
    ACTIVE_CYCLES = ['2016']



# cycle_list = [int(x) for x in ACTIVE_CYCLE]

class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # get all committees where there's outside spending
        for cycle in ACTIVE_CYCLES:
            print "handling cycle: %s" % cycle
            committee_list = Pac_Candidate.objects.filter(cycle=cycle).values('committee__fec_id').order_by('committee__fec_id').distinct()
            for ie_committee in committee_list:
                fec_id = ie_committee['committee__fec_id']
            
                total_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, cycle=cycle).aggregate(total=Sum('total_ind_exp'))['total']
            
                dem_support_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='D',support_oppose__iexact='S', cycle=cycle).aggregate(total=Sum('total_ind_exp'))['total']
            
                rep_support_ies  = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='R',support_oppose__iexact='S', cycle=cycle).aggregate(total=Sum('total_ind_exp'))['total']
            
                dem_oppose_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='D',support_oppose__iexact='O', cycle=cycle).aggregate(total=Sum('total_ind_exp'))['total']
            
                rep_oppose_ies = Pac_Candidate.objects.filter(committee__fec_id=fec_id, candidate__party__iexact='R',support_oppose__iexact='O', cycle=cycle).aggregate(total=Sum('total_ind_exp'))['total']
            
                print "id = %s total=%s support d = %s support r = %s oppose d = %s oppose r = %s" % (fec_id, total_ies, dem_support_ies, rep_support_ies, dem_oppose_ies, rep_oppose_ies)
            
                try:
                    this_committee = Committee_Overlay.objects.get(fec_id=fec_id, cycle=cycle)
                except Committee_Overlay.DoesNotExist:
                    continue
                
                this_committee.total_indy_expenditures = total_ies
                this_committee.ie_support_dems = dem_support_ies
                this_committee.ie_support_reps = rep_support_ies
                this_committee.ie_oppose_dems = dem_oppose_ies
                this_committee.ie_oppose_reps = rep_oppose_ies
            
                this_committee.save()
            