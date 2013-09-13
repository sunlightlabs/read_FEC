import datetime

from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404

from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from formdata.models import SkedE

FEED_LENGTH = 30

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
        return "%s - RECENT FILINGS" % obj.name
        
    def get_object(self, request, committee_id):
        return get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle='2014') 
        
    def description(self, obj):
        return "%s: Recent electronic campaign finance filings" % (obj.name)             

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id).order_by('-process_time')[:FEED_LENGTH]  

class CommitteeFormsFeed(FilingFeedBase): 
    form_list=[]

    def title(self, obj):
        return "%s - RECENT FORMS %s" % (obj.name, ", ".join(self.form_list) )

    def description(self, obj):
        return "Recent electronic campaign finance filings filed by %s" % (obj.name)        

    def get_object(self, request, committee_id, form_types):
        self.form_list=form_types.split("-")
        return get_object_or_404(Committee, fec_id=committee_id) 

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id, form_type__in=self.form_list).order_by('-process_time')[:FEED_LENGTH]
    
class FilingsFeed(FilingFeedBase):
    committee_list=[]
    
    def get_object(self, request, committee_ids):
        self.committee_list = committee_ids.split("-")
        return "Is this the timestamp?"

    def items(self, obj):
        return new_filing.objects.filter(fec_id__in=self.committee_list).order_by('-process_time')[:FEED_LENGTH]

class FilingsFormFeed(FilingFeedBase):
    committee_list=[]
    form_list=[]

    def get_object(self, request, committee_ids, form_types):
        self.committee_list = committee_ids.split("-")
        self.form_list=form_types.split("-")
        return "Is this the timestamp?"
    
    def description(self):
        return "Recent electronic finance filings of forms: " + " ".join(self.form_list)

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
        return datetime.datetime(thisdate.year, thisdate.month, thisdate.day)

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
        