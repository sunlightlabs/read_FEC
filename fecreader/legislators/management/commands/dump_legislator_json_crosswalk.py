import json, os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from datetime import date

from legislators.models import *

PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
crosswalk = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'leg_crosswalk.json')

class Command(BaseCommand):
    help = "Dump a crosswalk of legislators who have served somewhat recently."
    
    requires_model_validation = False

    def handle(self, *args, **options):
        outfile = open(crosswalk, 'w')
        
        return_array = []
        
        start_date_raw = "1/1/2006"
        start_date = dateparse(start_date_raw)
        terms = Term.objects.filter(start__gte=start_date)
        legislator_pks = Term.objects.filter(start__gte=start_date).order_by('legislator').values('legislator').distinct('legislator')
        
        for leg_pk in legislator_pks:
            leg = Legislator.objects.get(pk=leg_pk['legislator'])
            this_leg = {'last':leg.last_name, 'first':leg.first_name, 'official':leg.official_full or '', 'bioguide':leg.bioguide, 'thomas':leg.thomas or '', 'govtrack':leg.govtrack or '', 'opensecrets':leg.opensecrets or '', 'icpsr':leg.icpsr or ''}
            return_array.append(this_leg)
            
        outfile.write(json.dumps(return_array))
            
            