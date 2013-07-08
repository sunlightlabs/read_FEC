import json, os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse

from legislators.models import *

PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
committee_members_file = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'current_committee_members.json')

class Command(BaseCommand):
    help = "Dump a crosswalk of legislators who have served somewhat recently."
    
    requires_model_validation = False

    def handle(self, *args, **options):
        outfile = open(committee_members_file, 'w')
        
        return_array = []

        committees = Committee.objects.all()
        
        for committee in committees:
            
            committee_data = {'committee_type':committee.committee_type, 'name':committee.name, 'url':committee.url, 'thomas_id':committee.thomas_id, 'house_committee_id':committee.house_committee_id or ''}
            member_array = []
            members = CurrentCommitteeMembership.objects.filter(committee=committee)
            for member in members:
                member_data = {'bioguide':member.member.bioguide, 'rank':member.rank, 'party':member.party, 'title':member.title or '', 'first_name':member.member.first_name, 'last_name':member.member.last_name}
                member_array.append(member_data)
            committee_data['members']=member_array
            return_array.append(committee_data)
        outfile.write(json.dumps(return_array))
        