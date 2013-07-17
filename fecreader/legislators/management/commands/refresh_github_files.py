import os
import unicodedata
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
legislators_current = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'legislators-current.yaml')
committees_current = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'committees-current.yaml')
committee_membership_current = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'committee-membership-current.yaml')


def write_file(file_location, outfile_name):
    file_data =  requests.get(file_location)
    outfile = open(outfile_name, 'w')
    text = unicodedata.normalize('NFKD',file_data.text).encode('ascii','ignore')
    outfile.write(text)
    outfile.close()

class Command(BaseCommand):
    help = "Reload the committees file"
    requires_model_validation = False
    
    def handle(self, *args, **options):
#        write_file('https://raw.github.com/unitedstates/congress-legislators/master/legislators-current.yaml', legislators_current)
#        write_file('https://raw.github.com/unitedstates/congress-legislators/master/committees-current.yaml', committees_current)
        write_file('https://raw.github.com/unitedstates/congress-legislators/master/committee-membership-current.yaml', committee_membership_current)
        