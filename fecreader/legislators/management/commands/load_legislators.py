import yaml
import os

from dateutil.parser import parse as dateparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from legislators.models import *
from legislators.file_chunker import yamlChunker


PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')
current = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'legislators-current.yaml')
historic = os.path.join(PROJECT_ROOT, '..', 'legislators', 'data', 'legislators-historical.yaml')
 
def getmultidict(dictionary, key_list):
    try:
        return reduce(dict.get, key_list, dictionary)
    except TypeError:
        return None

def process_file(filename):
    print "Processing file %s" % (filename)
    token = 'id'
    chunker = yamlChunker(filename, token)

    count = 0
    hasnext=True
    while(hasnext):
        count += 1
        yamlrecord = chunker.next()
        #print "got yaml record: %s" % yamlrecord
        if not yamlrecord:
            hasnext=False
        else:
            if (count%100==0):
                print "Processed %s lines" % count
            legislator_yaml = yaml.load(yamlrecord)[0]
            bioguide = legislator_yaml['id']['bioguide']
            this_legislator = None
            try:
                this_legislator = Legislator.objects.get(bioguide=bioguide)
        
            except Legislator.DoesNotExist:
                this_legislator = Legislator.objects.create(
                    bioguide=getmultidict(legislator_yaml, ('id','bioguide')),
                    thomas=getmultidict(legislator_yaml, ('id','thomas')),
                    lis=getmultidict(legislator_yaml, ('id','lis')),                    
                    govtrack=getmultidict(legislator_yaml, ('id','govtrack')),
                    opensecrets=getmultidict(legislator_yaml, ('id','opensecrets')),
                    votesmart=getmultidict(legislator_yaml, ('id','votesmart')),                                                                                                    
                    icpsr=getmultidict(legislator_yaml, ('id','icpsr')),
                    cspan=getmultidict(legislator_yaml, ('id','cspan')),
                    wikipedia=getmultidict(legislator_yaml, ('id','wikipedia')),
                    house_history=getmultidict(legislator_yaml, ('id','house_history')),
                    bioguide_previous=getmultidict(legislator_yaml, ('id','bioguide_previous')),                
                    first_name=getmultidict(legislator_yaml, ('name','first')),
                    middle_name=getmultidict(legislator_yaml, ('name','middle')),
                    last_name=getmultidict(legislator_yaml, ('name','last')),
                    suffix=getmultidict(legislator_yaml, ('name','suffix')),                                                                            
                    nickname=getmultidict(legislator_yaml, ('name','nickname')), 
                    official_full=getmultidict(legislator_yaml, ('name','official_full')),
                    gender = getmultidict(legislator_yaml, ('bio','gender')),
                    birthday = getmultidict(legislator_yaml, ('bio','birthday')), 
                    religion = getmultidict(legislator_yaml, ('bio','religion'))
                )
                #print "Added %s" % (this_legislator)
                
            # fec id list:
            fecs = getmultidict(legislator_yaml, ('id','fec')),
            if fecs:    
                for this_fec in fecs:
                    if this_fec:
                        this_id = this_fec[0]
                        (this_fec, created) = fec.objects.get_or_create(legislator=this_legislator, fec_id=this_id)

            # terms
            terms = legislator_yaml.get('terms')
            if terms:
                for term in terms:
                    term_type = term.get('type')
                    start = term.get('start')
                    if start:
                        start = dateparse(start)                    
                    end = term.get('end')
                    if end:
                        end = dateparse(end)
                    state = term.get('state')
                    district = term.get('district')
                    party = term.get('party')
                    url = term.get('url')
                    address = term.get('address')
                    term_class = term.get('class')
                
                
                    (this_term, created) = Term.objects.get_or_create(legislator=this_legislator, term_type=term_type, start=start, end=end, state=state, district=district, term_class=term_class, party=party, url=url, address=address)
               
        
            # other names
            other_names = legislator_yaml.get('other_names')
            if other_names:
                for other_name in other_names:
                    first_name = other_name.get('first')
                    middle_name = other_name.get('middle')
                    last_name = other_name.get('last')
                    start = other_name.get('start')
                    if start:
                        start = dateparse(start)
                    end = other_name.get('end')
                    if end:
                        end = dateparse(end)                    
                
                
                    (this_other_name, created) = Other_Names.objects.get_or_create(legislator=this_legislator, first_name=first_name, last_name=last_name, middle_name=middle_name, start=start, end=end)
                
class Command(BaseCommand):
    help = "Load current and historic legislators from yaml files. This is not efficient, because it checks for the existence of each separate piece of data before loading, and quite slow, because it slurps and parses the whole historical file whole."
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        process_file(current)
        process_file(historic)