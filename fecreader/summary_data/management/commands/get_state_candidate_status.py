# show candidate status as json object suitable for human editing. 

import json

from optparse import make_option

from summary_data.models import District, Candidate_Overlay

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Regenerate the static competitive primary page."
    requires_model_validation = False
    
    
    option_list = BaseCommand.option_list + (
            make_option('--state',
                        action='store',
                        dest='state',
                        help="State to process"),
            )
    
    def handle(self, *args, **options):

        state = options['state']
        assert state, "No state given"
        #print "Checking candidate status='%s'" % (state)
        candidate_list = []

        races = District.objects.filter(state=state, election_year=2014).order_by('office', 'office_district')
    
        for race in races:
                #print "Handling race %s" % (race)
                  
                candidates = Candidate_Overlay.objects.filter(district=race).exclude(not_seeking_reelection=True).order_by('party', 'name')
                
                for candidate in candidates:
                    candidate_list.append({"id":candidate.pk, "fec_id":candidate.fec_id, "is_incumbent":candidate.is_incumbent, "name":candidate.name, "party":candidate.party, "office":candidate.office, "district":candidate.office_district, "candidate_status":candidate.candidate_status})


        print json.dumps(candidate_list, sort_keys=True, indent=4, separators=(',', ': ')) 