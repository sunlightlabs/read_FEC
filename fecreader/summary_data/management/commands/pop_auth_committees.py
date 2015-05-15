from django.core.management.base import BaseCommand, CommandError
from summary_data.models import Authorized_Candidate_Committees
from ftpdata.models import CandComLink, Committee, Candidate
from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = ['2016']

class Command(BaseCommand):
    help = "Set the authorized candidate committees"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        ccls = CandComLink.objects.filter(cycle=CURRENT_CYCLE, cmte_dsgn__in=['A', 'P'], fec_election_yr=int(CURRENT_CYCLE))
        
        for ccl in ccls:
            print "handling %s %s" % (ccl.cmte_id, ccl.cand_id)
            try:
                acc = Authorized_Candidate_Committees.objects.get(candidate_id=ccl.cand_id, committee_id=ccl.cmte_id, cycle=int(CURRENT_CYCLE))
            except Authorized_Candidate_Committees.DoesNotExist:
                
                cm_name = None
                try:
                    cm = Committee.objects.get(cycle=CURRENT_CYCLE, cmte_id=ccl.cmte_id)
                    cm_name = cm.cmte_name
                except Committee.DoesNotExist:
                    print "Committee object doesn't exist for id=%s cand_id=%s" % (ccl.cmte_id, ccl.cand_id)
                
                acc = Authorized_Candidate_Committees.objects.create(
                    candidate_id = ccl.cand_id,
                    committee_id = ccl.cmte_id,
                    committee_name = cm_name,
                    com_type = ccl.cmte_tp,
                    is_pcc = ccl.cmte_dsgn == 'P',
                    cycle = CURRENT_CYCLE
                )
        