from django.core.management.base import BaseCommand, CommandError
from summary_data.models import Incumbent
from legislators.models import *
from ftpdata.models import Candidate
from summary_data.models import Candidate_Overlay
from datetime import date

def set_fec_id(this_fec_id):
    try:
        
        ftpcandidate = Candidate.objects.filter(cand_id = this_fec_id).order_by('-cycle')[0]
    except IndexError:
        print "No candidate found in master file for id=%s" % (this_fec_id)
        return
    print "Got cycle: %s" % (ftpcandidate.cycle)
    this_incumbent, created = Incumbent.objects.get_or_create(fec_id=this_fec_id)
    this_incumbent.cycle='2016'
    this_incumbent.name = ftpcandidate.cand_name
    this_incumbent.fec_id = this_fec_id
    this_incumbent.state = ftpcandidate.cand_office_st
    this_incumbent.office_district = ftpcandidate.cand_office_district
    this_incumbent.office = ftpcandidate.cand_office
    this_incumbent.is_incumbent=True
    this_incumbent.save()
    
    # Now set the incumbent flag in candidate_overlay
    try:
        this_co = Candidate_Overlay.objects.get(fec_id=this_fec_id, cycle='2016')
        this_co.is_incumbent = True
        this_co.save()
        #print "set incumbent %s, %s" % (ftpcandidate.cand_name, this_fec_id)
    except Candidate_Overlay.DoesNotExist:
        pass
        print "Missing candidate: %s, %s" % (ftpcandidate.cand_name, this_fec_id)
    
    
    

class Command(BaseCommand):
    help = "set the incumbent challenger status based on us congress"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        

        legislator_pks = Term.objects.filter(end__gte=date.today()).order_by('legislator').values('legislator').distinct('legislator')
        for leg_pk in legislator_pks:
            leg = Legislator.objects.get(pk=leg_pk['legislator'])
            
            
            fec_id_list = fec.objects.filter(legislator=leg)
            if len(fec_id_list) != 1:
                terms = Term.objects.filter(end__gte=date.today(), legislator=leg)
                if terms:
                    term = terms[0]
                    chamber = term.term_type
                    possible_ids = []
                
                    #print "not 1 fec id: %s - chamber: %s" % (leg, chamber)
                    for fec_id in fec_id_list:
                        tfi = fec_id.fec_id
                        #print "fec_id is %s" % (tfi)
                        if (chamber == 'rep' and tfi.startswith('H')) or (chamber == 'sen' and tfi.startswith('S')):
                            #print "possible fec_id %s" % (tfi)
                            possible_ids.append(tfi)
                
                    if len(possible_ids) == 1:
                        # we've only got one candidate, so use it
                        set_fec_id(possible_ids[0])
                    
                    else: 
                        #print "Still have multiple candidates"
                        # go through each of them
                        possible_ids_2 = []
                        for fec_id in possible_ids:
                            try:
                                Candidate.objects.get(cand_id=fec_id, cycle=2014)
                                possible_ids_2.append(fec_id)
                            except Candidate.DoesNotExist:
                                pass
                    
                        if len(possible_ids_2) == 0:
                            print "*2: no possible candidates %s" % (leg)
                        elif len(possible_ids_2) == 1:
                            set_fec_id(possible_ids_2[0])
                        else:
                            print "*2: more than one possible candidate with current id found %s : %s" % (leg, possible_ids_2)
                            possible_ids_3 = []
                            for fec_id in possible_ids_3:
                                try:
                                    Candidate.objects.get(cand_id=fec_id, cand_election_year=2014)
                                    possible_ids_3.append(fec_id)
                                except Candidate.DoesNotExist:
                                    pass
                            if len(possible_ids_3) == 0:
                                print "*3: no possible candidates %s" % (leg)
                            elif len(possible_ids_3) == 1:
                                set_fec_id(possible_ids_3[0])
                            else:
                                print "*3: more than one possible candidate with current id found %s : %s" % (leg, possible_ids_3)
                    
                
            else:
                this_fec_id = fec_id_list[0].fec_id
                #print "%s %s" % (this_fec_id, leg)
                set_fec_id(this_fec_id)
                