from django.core.management.base import BaseCommand, CommandError
from summary_data.models import Authorized_Candidate_Committees
from ftpdata.models import CandComLink, Committee, Candidate


election_year = 2014
cycle = str(election_year)

class Command(BaseCommand):
    help = "Set the authorized candidate committees"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        ccls = CandComLink.objects.filter(cycle=election_year, cmte_dsgn__in=['A', 'P'])
        
        for ccl in ccls:
            try:
                acc = Authorized_Candidate_Committees.objects.get(candidate_id=ccl.cand_id, committee_id=ccl.cmte_id)
            except Authorized_Candidate_Committees.DoesNotExist:
                
                cm_name = None
                try:
                    cm = Committee.objects.get(cycle=election_year, cmte_id=ccl.cmte_id)
                    cm_name = cm.cmte_name
                except Committee.DoesNotExist:
                    pass
                
                acc = Authorized_Candidate_Committees.objects.create(
                    candidate_id = ccl.cand_id,
                    committee_id = ccl.cmte_id,
                    committee_name = cm_name,
                    com_type = ccl.cmte_tp,
                    is_pcc = ccl.cmte_dsgn == 'P'
                )

        
        