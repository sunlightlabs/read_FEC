import datetime
import pytz

from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django import template

from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay, District, Candidate_Overlay
from formdata.models import SkedE
from django.conf import settings

CURRENT_CYCLE = settings.CURRENT_CYCLE

FEED_LENGTH = 30
nyt = pytz.timezone('America/New_York')

class FilingFeedBase(Feed):
    description_template = 'feeds/fec_filing_description.html'

    # What is this used for?
    def link(self, obj):
        return 'http://realtime.influenceexplorer.com/newest-filings/'

    def description(self):
        return "Recent electronic campaign finance filings."
    
    def item_title(self, item):
        return  "%s - %s" % (item.committee_name, item.get_form_name().upper() )
        
    def item_pubdate(self, item):
        return item.process_time

    def title(self):
        return "RECENT FILINGS FROM VARIOUS COMMITTEES"

class FilingFeed(FilingFeedBase): 
       
    def title(self, obj):
        return "%s %s CYCLE RECENT FILINGS" % (CURRENT_CYCLE, obj.name)
        
    def get_object(self, request, committee_id):
        return get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=CURRENT_CYCLE) 
        
    def description(self, obj):
        return "%s: Recent electronic campaign finance filings (%s cycle)" % (obj.name, CURRENT_CYCLE)             

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id).order_by('-process_time')[:FEED_LENGTH]  

class CommitteeFormsFeed(FilingFeedBase): 
    form_list=[]

    def title(self, obj):
        return "%s - RECENT FORMS %s" % (obj.name, ", ".join(self.form_list) )

    def description(self, obj):
        return "Recent electronic campaign finance filings filed by %s (%s cycle)" % (obj.name, CURRENT_CYCLE)        

    def get_object(self, request, committee_id, form_types):
        self.form_list=form_types.split("-")
        return get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=CURRENT_CYCLE) 

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id, form_type__in=self.form_list).order_by('-process_time')[:FEED_LENGTH]
    
class FilingsFeed(FilingFeedBase):
    committee_list=[]
    
    def get_object(self, request, committee_ids):
        self.committee_list = committee_ids.split("-")
        return "Is this the timestamp?"

    def items(self, obj):
        return new_filing.objects.filter(fec_id__in=self.committee_list, cycle=CURRENT_CYCLE).order_by('-process_time')[:FEED_LENGTH]

class FilingsFormFeed(FilingFeedBase):
    committee_list=[]
    form_list=[]

    def get_object(self, request, committee_ids, form_types):
        self.committee_list = committee_ids.split("-")
        self.form_list=form_types.split("-")
        return "Is this the timestamp?"
    
    def description(self):
        return "Recent electronic finance filings of forms (" + CURRENT_CYCLE + " cycle): " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(fec_id__in=self.committee_list, form_type__in=self.form_list).order_by('-process_time')[:FEED_LENGTH]
        
class FilingsForms(FilingFeedBase):
    form_list=[]

    def get_object(self, request, form_types):
        self.form_list=form_types.split("-")
        return "Is this the timestamp?"   
             
    def description(self):
        return "Recent electronic finance filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(form_type__in=self.form_list).order_by('-process_time')[:FEED_LENGTH]    
    
class SuperpacsForms(FilingFeedBase):
    form_list = []
    
    def get_object(self, request, form_types):
        self.form_list=form_types.split("-")
        return "Is this the timestamp?"
    
    def description(self):
        return "Superpac filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(form_type__in=self.form_list, is_superpac=True).order_by('-process_time')[:FEED_LENGTH]    
    
    def title(self, obj):
        return "Super PAC filings -- forms: " + " ".join(self.form_list)
    
class IEFeedBase(Feed):
    description_template = 'feeds/independent_expenditure_description.html'

    # What is this used for?
    def link(self, obj):
        return 'http://realtime.influenceexplorer.com/independent-expenditures/'

    def description(self):
        return "Recent independent expenditures"

    def item_title(self, item):
        
        return  "%s - independent expenditure - %s %s" % (item.committee_name, item.supporting_opposing(), item.candidate_name_checked)

    def item_pubdate(self, item):
        thisdate = item.expenditure_date_formatted
        try:
            return datetime.datetime(thisdate.year, thisdate.month, thisdate.day)
        except AttributeError:
            return None
        
    def title(self):
        return "RECENT INDEPENDENT EXPENDITURES"


class IEFeed(IEFeedBase): 
    description_template = 'feeds/independent_expenditure_description.html'

    def title(self):
        return "RECENT FILINGS FEED" 

    def get_object(self, request):
        return "" 

    def description(self, obj):
        return "Recent independent expenditures"
        
    def items(self, obj):
        return SkedE.objects.filter(superceded_by_amendment=False).order_by('-expenditure_date_formatted').select_related('district_checked')[:FEED_LENGTH]
        
class IEFeedMin(IEFeedBase): 
    description_template = 'feeds/independent_expenditure_description.html'
    feed_min = 0

    def title(self):
        return "RECENT FILINGS FEED" 

    def get_object(self, request, min_spent):
        print "Got min spent: %s" % (min_spent)
        self.feed_min = int(min_spent)
        return "" 

    def description(self, obj):
        return "Recent independent expenditures over $%s" % (self.feed_min) 

    def items(self, obj):
        #SkedE.objects.filter(superceded_by_amendment=False, expenditure_amount__gte=self.feed_min).order_by('-expenditure_date_formatted').select_related('district_checked')[:FEED_LENGTH]
        return SkedE.objects.filter(superceded_by_amendment=False, expenditure_amount__gte=self.feed_min).order_by('-expenditure_date_formatted').select_related('district_checked')[:FEED_LENGTH]


class MixedFeed(Feed):
    """ A feed that includes itemized expenditures in a race, as well as candidate filings. """
    
    #description_template = 'feeds/independent_expenditure_description.html'
    race_name = None
    race_id = None
    term_class = None
    state = None
    office = None
    office_district = None
    election_year = None
    is_special_election = False
    district_object = None
    committee_list = None
    candidate_list = None
    filing_description_template = None
    ie_description_template = None
    
    def get_object(self, request, election_year, office, state, office_descriptor):
        # class-based views made me do it. Why isn't this in the init? Because args get passed to get_object, I guess. But who knows?
        self.office = office
        self.election_year = election_year
        self.state = state
        # we have to render stuff differently depending what kinda content it is. Doubtless there's a more elegant way of doing this. 
        # instead, just get the two templates we might use, and render with the right one. 
        self.filing_description_template = template.loader.get_template('feeds/fec_filing_description.html')
        self.ie_description_template = template.loader.get_template('feeds/independent_expenditure_description.html')
        
        
        possible_districts = District.objects.filter(election_year=election_year, office=office)
        if office == 'S':
            self.term_class = office_descriptor
            self.district_object = possible_districts.get(state=self.state, term_class=self.term_class)
            
        elif office == 'H':
            self.office_district = office_descriptor
            self.district_object = possible_districts.get(state=self.state, office_district=self.office_district)
            
        """ UNDEFINED - WE DON'T HAVE PRESIDENTIAL 'DISTRICT' DEFINED FOR NOW. 
        elif office == 'P':
        """
        self.race_name = self.district_object.district_formatted()
        self.race_id = self.district_object.pk
        """ Also not defined
        self.is_special_election = self.district_object.
        """
        
        candidates = Candidate_Overlay.objects.filter(district=self.district_object)
        candidate_list = [x.get('fec_id') for x in candidates.values('fec_id')]
        self.candidate_list = candidate_list
        
        committees = Committee_Overlay.objects.filter(curated_candidate__district=self.district_object)
        committee_list = [x.get('fec_id') for x in committees.values('fec_id')]
        self.committee_list = committee_list
        print "got committee list: %s" % (committee_list)
        
    
    # What is this used for?
    def link(self, obj):
        return 'http://realtime.influenceexplorer.com/races/'

    def description(self):
        return "Recent filings and independent expenditures in race: %s" % (self.race_name)

    def item_title(self, item):
        return item['title']
                
    def item_pubdate(self, item):
        return item['pubdate']
        
    def item_description(self, item):
        return item['description']
    def item_link(self, item):
        return item['link']

    def title(self):
        return "RACE FEED"

    def items(self, obj):
        # get filings
        nfs = new_filing.objects.filter(fec_id__in=self.committee_list).order_by('-process_time')[:FEED_LENGTH]    
        nf_array = []
        for nf in nfs:
            
            description = self.filing_description_template.render(template.Context({'obj': nf}))
            title = "%s - %s" % (nf.committee_name, nf.get_form_name().upper() )
            nf_array.append({'pubdate': nf.process_time, 'title':title, 'description':description, 'link':nf.get_absolute_url()})
        
        
        skedes = SkedE.objects.filter(candidate_id_checked__in=self.candidate_list, superceded_by_amendment=False).order_by('-expenditure_date_formatted').select_related('district_checked')[:FEED_LENGTH]
        skede_array = []
        for se in skedes:
            
            description = self.ie_description_template.render(template.Context({'obj': se}))
            title = "%s - independent expenditure - %s %s" % (se.committee_name, se.supporting_opposing(), se.candidate_name_checked)
            thisdate = se.expenditure_date_formatted
            pubdate = datetime.datetime(thisdate.year, thisdate.month, thisdate.day, 0, 0, 0, 0, nyt)
            skede_array.append({'pubdate': pubdate, 'title':title, 'description':description, 'link':se.get_absolute_url()})
        
        # now combine the array, sort them by pubdate, and return the top ones
        new_array = skede_array + nf_array
        new_array.sort(key=lambda x: x['pubdate'], reverse=True)
        return new_array[:FEED_LENGTH]