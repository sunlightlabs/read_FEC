# takes the file spit out by get_state_candidate_status and set the candidate status, party and name. Uses the primary key to lookup the candidates. All other aspects of the json are ignored.

import json

from optparse import make_option

from summary_data.models import District, Candidate_Overlay

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Set the candidate status of candidates. Uses the file spit out by get_state_candidate_status."
    requires_model_validation = False
    
    
    option_list = BaseCommand.option_list + (
            make_option('--file',
                        action='store',
                        dest='file',
                        help="file to process"),
            )
    
    def handle(self, *args, **options):

        filepath = options['file']
        assert filepath, "No json file given"

        fileread = open(filepath, 'r').read()
        filejson = json.loads(fileread)
        
        for candidate in filejson:
            if candidate['candidate_status']:
                print "setting candidate status to %s for %s - %s" % (candidate['candidate_status'], candidate['name'], candidate['fec_id'])
                cand_overlay = Candidate_Overlay.objects.get(pk=candidate['id'])
                assert (cand_overlay.fec_id == candidate['fec_id']), "mismatch in fec id between %s and %s" % (cand_overlay.name, candidate['name'])
                cand_overlay.candidate_status = candidate['candidate_status']
                cand_overlay.name = candidate['name']
                cand_overlay.party = candidate['party']
                
                cand_overlay.save()