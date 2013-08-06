from datetime import date

import django_filters

from django.db.models import Sum, Count, Q

from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from rest_framework import viewsets
from rest_framework import generics
from api.serializers import NFSerializer, COSerializer

PAGINATION_LENGTH = 100
class NFFilter(django_filters.FilterSet):
    
    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='tot_raised', lookup_type='gte')
    min_spent = django_filters.NumberFilter(name='tot_spent', lookup_type='gte')
    min_coh = django_filters.NumberFilter(name='coh_end', lookup_type='gte')

    
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


def periodTypeFilter(queryset, querydict):
    try:
        period_type=querydict['period_type']
        if period_type.startswith('Q'):
            if period_type == 'Q1':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,1,1), coverage_to_date=date(2013,3,31))|Q(coverage_from_date=date(2014,1,1), coverage_to_date=date(2014,3,31)))
        
            elif period_type == 'Q2':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,4,1), coverage_to_date=date(2013,6,30))|Q(coverage_from_date=date(2014,4,1), coverage_to_date=date(2014,6,30)))

            elif period_type == 'Q3':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,7,1), coverage_to_date=date(2013,9,31))|Q(coverage_from_date=date(2014,7,1), coverage_to_date=date(2014,9,31)))

            elif period_type == 'Q4':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,10,1), coverage_to_date=date(2013,12,31))|Q(coverage_from_date=date(2014,10,1), coverage_to_date=date(2014,9,31)))


        elif period_type.startswith('M'):
                        
            if period_type == 'M1':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,1,1), coverage_to_date=date(2013,1,31))|Q(coverage_from_date=date(2014,1,1), coverage_to_date=date(2014,1,31)))

            elif period_type == 'M2':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,2,1), coverage_to_date=date(2013,2,28))|Q(coverage_from_date=date(2014,2,1), coverage_to_date=date(2014,2,28)))

            elif period_type == 'M3':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,3,1), coverage_to_date=date(2013,3,31))|Q(coverage_from_date=date(2014,3,1), coverage_to_date=date(2014,3,31)))

            elif period_type == 'M4':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,4,1), coverage_to_date=date(2013,4,30))|Q(coverage_from_date=date(2014,4,1), coverage_to_date=date(2014,4,30)))

            elif period_type == 'M5':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,5,1), coverage_to_date=date(2013,5,31))|Q(coverage_from_date=date(2014,5,1), coverage_to_date=date(2014,5,31)))

            elif period_type == 'M6':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,6,1), coverage_to_date=date(2013,6,30))|Q(coverage_from_date=date(2014,6,1), coverage_to_date=date(2014,6,30)))

            elif period_type == 'M7':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,7,1), coverage_to_date=date(2013,7,31))|Q(coverage_from_date=date(2014,7,1), coverage_to_date=date(2014,7,31)))

            elif period_type == 'M8':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,8,1), coverage_to_date=date(2013,8,31))|Q(coverage_from_date=date(2014,8,1), coverage_to_date=date(2014,8,31)))

            elif period_type == 'M9':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,9,1), coverage_to_date=date(2013,9,30))|Q(coverage_from_date=date(2014,9,1), coverage_to_date=date(2014,9,30)))

            elif period_type == 'M10':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,10,1), coverage_to_date=date(2013,10,31))|Q(coverage_from_date=date(2014,10,1), coverage_to_date=date(2014,10,31)))

            elif period_type == 'M11':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,11,1), coverage_to_date=date(2013,11,30))|Q(coverage_from_date=date(2014,11,1), coverage_to_date=date(2014,11,30)))

            elif period_type == 'M12':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,12,1), coverage_to_date=date(2013,12,31))|Q(coverage_from_date=date(2014,12,1), coverage_to_date=date(2014,12,31)))

        elif period_type.startswith('S'):

            if period_type == 'S1':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,1,1), coverage_to_date=date(2013,6,30))|Q(coverage_from_date=date(2014,1,1), coverage_to_date=date(2014,6,30)))
        
            elif period_type == 'S2':
                queryset = queryset.filter(Q(coverage_from_date=date(2013,7,1), coverage_to_date=date(2013,12,31))|Q(coverage_from_date=date(2014,7,1), coverage_to_date=date(2014,12,31)))
        
    except KeyError:
        pass
    return queryset

def reportTypeFilter(queryset, querydict):
    try:
        report_type=querydict['report_type']
        if report_type == 'monthly':
            queryset = queryset.filter(form_type__in=['F3X', 'F3XN', 'F3XA', 'F3', 'F3A', 'F3N', 'F3P', 'F3PA', 'F3PN'])
            
        elif report_type == 'ies':
            queryset = queryset.filter(form_type__in=['F5', 'F5N', 'F5A', 'F24', 'F24A', 'F24N'])
            
        elif report_type == 'F6':
            queryset = queryset.filter(form_type__in=['F6', 'F6N', 'F6A'])
            
        elif report_type == 'F9':
            queryset = queryset.filter(form_type__in=['F9', 'F9N', 'F9A'])
            
        elif report_type == 'F2':
            queryset = queryset.filter(form_type__in=['F2', 'F2N', 'F2A'])
    except KeyError:
        pass
    
    return queryset
                        
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
        self.queryset = reportTypeFilter(self.queryset, self.request.GET)
        self.queryset = periodTypeFilter(self.queryset, self.request.GET)
        
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