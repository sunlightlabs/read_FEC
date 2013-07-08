import yaml
import os

from dateutil.parser import parse as dateparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from legislators.models import *
from legislators.file_chunker import yamlChunker


PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
current = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'committees-current.yaml')


def process_file(filename):
    print "Processing file %s" % (filename)
    token = 'type'
    chunker = yamlChunker(filename, token)
    
    count = 0
    hasnext=True
    while(hasnext):
        count += 1
        yamlrecord = chunker.next()
        print "got yaml record: %s" % yamlrecord
        if not yamlrecord:
            hasnext=False
        else:
            if (count%100==0):
                print "Processed %s lines" % count
            committee_yaml = yaml.load(yamlrecord)[0]
            thomas_id = committee_yaml['thomas_id']
            try:
                this_committee = Committee.objects.get(thomas_id=thomas_id)
            except Committee.DoesNotExist:
                this_committee = Committee.objects.create(
                    committee_type = committee_yaml['type'],
                    name = committee_yaml['name'],
                    thomas_id = committee_yaml['thomas_id'],
                    house_committee_id = committee_yaml.get('house_committee_id'),
                    url = committee_yaml.get('url') or '')

class Command(BaseCommand):
    help = "Load current committees from yaml files. This is not efficient, because it checks for the existence of each separate piece of data before loading."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        process_file(current)
