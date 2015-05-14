# load both the house and senate ratings
# assumes the files have already been downloaded
from lxml import etree
from StringIO import StringIO

from django.core.management.base import BaseCommand, CommandError

from rothenberg.models import HouseRace, SenateRace


from django.conf import settings

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'

#ROTHENBERG_HOUSE_FILE  = settings.ROTHENBERG_HOUSE_FILE
#ROTHENBERG_SENATE_FILE  = settings.ROTHENBERG_SENATE_FILE

ROTHENBERG_HOUSE_FILE = "rothenberg/data/house.xml"
ROTHENBERG_SENATE_FILE = "rothenberg/data/senate.xml"

def parse_senate_line(elt):
    result = {}
    result['state'] = elt.find('state').text
    result['seat_class'] = elt.find('class').text
    rating = elt.find('rating')
    result['rating_id'] = rating.find('id').text
    result['rating_segment'] = rating.find('segment').text
    result['rating_label'] = rating.find('label').text
    result['incumbent'] = elt.find('incumbent').text
    return result

def parse_house_line(elt):
    result = {}
    result['state'] = elt.find('state').text
    result['district'] = elt.find('district').text
    rating = elt.find('rating')
    result['rating_id'] = rating.find('id').text
    result['rating_label'] = rating.find('label').text
    result['incumbent'] = elt.find('incumbent').text
    return result
        
def load_house(filepath, cycle):
    xmldata = open(filepath, 'r').read()
    tree = etree.parse(StringIO(xmldata))
    for elt in tree.getiterator('race'):
        result = parse_house_line(elt)
        print result
        try:
            thisrace = HouseRace.objects.get(state=result['state'],district=result['district'], cycle=cycle)
            thisrace.rating_id = result['rating_id']
            thisrace.rating_label = result['rating_label']
            thisrace.save()
            
        except HouseRace.DoesNotExist:
            result['cycle'] = cycle
            HouseRace.objects.create(**result)
            

def load_senate(filepath, cycle):
    xmldata = open(filepath, 'r').read()
    tree = etree.parse(StringIO(xmldata))
    for elt in tree.getiterator('race'):
        result = parse_senate_line(elt)
        print result
        try:
            thisrace = SenateRace.objects.get(state=result['state'],seat_class=result['seat_class'], cycle=cycle)
            thisrace.rating_id = result['rating_id']
            thisrace.rating_label = result['rating_label']
            thisrace.save()

        except SenateRace.DoesNotExist:
            result['cycle'] = cycle
            SenateRace.objects.create(**result)
        
        
        
class Command(BaseCommand):
    help = "load both the house and senate ratings"
    requires_model_validation = False

    def handle(self, *args, **options):
        print "loading house..."
        load_house(ROTHENBERG_HOUSE_FILE, CURRENT_CYCLE)
        print "loading senate..."
        load_senate(ROTHENBERG_SENATE_FILE, CURRENT_CYCLE)
        
"""
 can run custom loads by specifying an earlier file and cycle:

from rothenberg.management.commands.load_rothenberg_ratings import load_house, load_senate
HOUSE_FILE = 'rothenberg/data/backups/house10-22-2014-04-09.xml'
SENATE_FILE = 'rothenberg/data/backups/senate10-22-2014-04-09.xml'
CURRENT_CYCLE = '2014'
load_house(HOUSE_FILE, CURRENT_CYCLE)
load_senate(SENATE_FILE, CURRENT_CYCLE)

"""


"""