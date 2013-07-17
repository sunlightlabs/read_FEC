import yaml
import os

from dateutil.parser import parse as dateparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from legislators.models import *

PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
current_membership = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'committee-membership-current.yaml')


def process_file(filename):
    print "Processing file %s" % (filename)
    # read the whole file -- slow, but...
    membership_records = yaml.load(open(filename, 'r'))
    #print membership_records
    for membership in membership_records:
        # We only care about committees, not subcomittees. These have 4-letter thomas_ids. The subcommittees are \w{4}\d{2}
        if len(membership)==4:
            print membership
            committee = Committee.objects.get(thomas_id=membership)
            print "Processing committee %s" % (committee)
            for member in membership_records[membership]:
                bioguide = member['bioguide']
                
                legislator = Legislator.objects.get(bioguide=bioguide)
                print "Adding %s" % (legislator.last_name)
                try:
                    CurrentCommitteeMembership.objects.get(committee=committee, member=legislator)
                except CurrentCommitteeMembership.DoesNotExist:
                    CurrentCommitteeMembership.objects.create(
                        committee=committee,
                        member=legislator,
                        rank = member['rank'],
                        party = member['party'],
                        title = member.get('title'),
                        )
                
class Command(BaseCommand):
    help = "Load current committees from yaml files. This is not efficient, because it checks for the existence of each separate piece of data before loading."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        process_file(current_membership)