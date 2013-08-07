from datetime import date


from django.db.models import Sum, Count, Q

from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from rest_framework import viewsets
from rest_framework import generics
from api.serializers import NFSerializer, COSerializer
from api.filters import NFFilter, COFilter, periodTypeFilter, reportTypeFilter, orderingFilter, multiCommitteeTypeFilter, multiCTypeFilter, filingTimeFilter

PAGINATION_LENGTH = 100

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
        self.queryset = filingTimeFilter(self.queryset, self.request.GET)
        
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