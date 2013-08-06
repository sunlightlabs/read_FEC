

import django_filters

from django.db.models import Sum, Count

from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from rest_framework import viewsets
from rest_framework import generics
from api.serializers import NFSerializer, COSerializer

PAGINATION_LENGTH = 100
class NFFilter(django_filters.FilterSet):
    
    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='tot_raised', lookup_type='gte')
    
    filed_before = django_filters.DateFilter(name='filed_date', lookup_type='lte') 
    filed_after = django_filters.DateFilter(name='filed_date', lookup_type='gte') 
    

    class Meta:
        model = new_filing
        fields = ['fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present']
        

class COFilter(django_filters.FilterSet):

    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='total_receipts', lookup_type='gte')



    class Meta:
        model = Committee_Overlay
        fields = ['fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype']
                

def orderingFilter(queryset, querydict, fields):
    """
    Only works if the ordering hasn't already been set. Which it hasn't, but... 
    """
    try:
        ordering=querydict['ordering']
        print "ordering is %s" % ordering
        if ordering.lstrip('-') in fields:
            orderlist = [ordering]
            print "order list is: %s" % orderlist
            queryset = queryset.order_by(*orderlist)
        
    except KeyError:
        pass
    
    return queryset

# create a phony keyword committee class that is just a list of committee types allowed
# so superpacs would be 'UO' -- but if we wanted to included hybrids, it would be 'UOVW'
def multiCommitteeTypeFilter(queryset, querydict):
    try:
        committee_class = querydict['committee_class']
        committee_class = committee_class.upper()
        committee_type_list = list(committee_class)
        queryset = queryset.filter(committee_type__in=committee_type_list)
        
    except KeyError:
        pass
        
    return queryset

# variant with different name for committee type.
def multiCTypeFilter(queryset, querydict):
    try:
        committee_class = querydict['committee_class']
        committee_class = committee_class.upper()
        committee_type_list = list(committee_class)
        queryset = queryset.filter(ctype__in=committee_type_list)

    except KeyError:
        pass

    return queryset

nf_orderable_fields = ['committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent']
class NFViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows new filings to be viewd.
    """
    queryset = new_filing.objects.all()
    serializer_class = NFSerializer
    filter_class = NFFilter
    paginate_by = PAGINATION_LENGTH
    
    
    
    def get_queryset(self):  
        # It seems like there should be a better way to chain filters together than this
        # the django-rest-framework viewset approach appear to allow just one filter though
        # so just apply these filters before the filter_class sees it. 
        self.queryset = orderingFilter(self.queryset, self.request.GET, nf_orderable_fields)
        self.queryset =  multiCommitteeTypeFilter(self.queryset, self.request.GET)
        
        return self.queryset
        

co_orderable_fields = ['fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype']

class COViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows committee_overlays to be viewd.
    """
    queryset = Committee_Overlay.objects.all()
    serializer_class = COSerializer
    filter_class = COFilter
    paginate_by = PAGINATION_LENGTH
    

    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.       
        self.queryset = orderingFilter(self.queryset, self.request.GET, co_orderable_fields)
        self.queryset =  multiCTypeFilter(self.queryset, self.request.GET)
        return self.queryset