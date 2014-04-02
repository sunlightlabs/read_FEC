from datetime import date


from django.db.models import Sum, Count, Q

from datetime import date
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay, DistrictWeekly, District
from formdata.models import SkedE
from rest_framework import viewsets
from rest_framework import generics
from api.serializers import NFSerializer, COSerializer, SkedESerializer, OSSerializer, DWSerializer, DistrictSerializer
from api.filters import *
from rest_framework_csv import renderers as r
from rest_framework.settings import api_settings
from paginated_csv_renderer import PaginatedCSVRenderer

CYCLE_START=date(2013,1,1)

nf_orderable_fields = ['committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent']
class NFViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows new filings to be viewed.
    """
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 
    
    
    queryset = new_filing.nulls_last_objects.all()
    serializer_class = NFSerializer
    filter_class = NFFilter
    
    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100
    
    def get_queryset(self):  
        # It seems like there should be a better way to chain filters together than this
        # the django-rest-framework viewset approach appear to allow just one filter though
        # so just apply these filters before the filter_class sees it. 
        

        self.queryset = orderingFilter(self.queryset, self.request.GET, nf_orderable_fields)
        self.queryset = yearFilter(self.queryset, self.request.GET)
        self.queryset =  multiCommitteeTypeFilter(self.queryset, self.request.GET)
        self.queryset = reportTypeFilter(self.queryset, self.request.GET)
        self.queryset = periodTypeFilter(self.queryset, self.request.GET)
        self.queryset = filingTimeFilter(self.queryset, self.request.GET)
        self.queryset = committeeSearchSlow(self.queryset, self.request.GET)
        self.queryset = candidateidSearch(self.queryset, self.request.GET)
        
        return self.queryset
        

co_orderable_fields = ['fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype']

class COViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows committee_overlays to be viewed.
    """
    
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 
    
    queryset = Committee_Overlay.nulls_last_objects.all().select_related('curated_candidate')
    serializer_class = COSerializer
    filter_class = COFilter
    
    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100
            
    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.       
        self.queryset = orderingFilter(self.queryset, self.request.GET, co_orderable_fields)
        self.queryset =  multiCTypeFilter(self.queryset, self.request.GET)
        self.queryset =  candidateCommitteeSearchSlow(self.queryset, self.request.GET)
        return self.queryset
        


os_orderable_fields = ['fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype']

class OSViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows outside spenders to be viewed.
    """

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 

    queryset = Committee_Overlay.nulls_last_objects.filter(total_indy_expenditures__gt=0).order_by('-total_indy_expenditures')
    serializer_class = OSSerializer
    filter_class = OSFilter

    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100

    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.       
        self.queryset = orderingFilter(self.queryset, self.request.GET, os_orderable_fields)
        self.queryset =  multiCTypeFilter(self.queryset, self.request.GET)
        self.queryset =  candidateCommitteeSearchSlow(self.queryset, self.request.GET)
        return self.queryset



district_orderable_fields = ['total_spending', 'outside_spending', 'cycle_week_number', 'state', 'next_election_date']

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows weekly district summaries to be viewed.
    """

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 

    queryset = District.objects.all().order_by('-outside_spending')
    serializer_class = DistrictSerializer
    filter_class = DistrictFilter

    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100

    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.       
        self.queryset = orderingFilter(self.queryset, self.request.GET, district_orderable_fields)
        return self.queryset
    

dw_orderable_fields = ['total_spending', 'outside_spending', 'cycle_week_number']

class DWViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows weekly district summaries to be viewed.
    """

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 

    queryset = DistrictWeekly.nulls_last_objects.all().select_related('district').order_by('cycle_week_number', 'district__pk')
    serializer_class = DWSerializer
    filter_class = DWFilter

    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100

    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.       
        self.queryset = orderingFilter(self.queryset, self.request.GET, dw_orderable_fields)
        self.queryset = DWDistrictFilter(self.queryset, self.request.GET)
        self.queryset = weekFilter(self.queryset, self.request.GET)
        return self.queryset


skede_orderable_fields = ['expenditure_date_formatted', 'expenditure_amount', 'payee_state', 'committee_name', 'candidate_name_checked']

class SkedEViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows sked e items to be viewed.
    """
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer] 
    
    queryset = SkedE.nulls_last_objects.filter(superceded_by_amendment=False, expenditure_date_formatted__gte=CYCLE_START).exclude(memo_code='X')
    serializer_class = SkedESerializer
    filter_class = SkedEFilter
    
    def get_paginate_by(self):
            """
            Use smaller pagination for json/html than csv
            """
            if self.request.accepted_renderer.format == ('csv'):
                return 2000
            return 100

    def get_queryset(self):  
        # Again, this seems like a pretty weird way to do this.               
        self.queryset = orderingFilter(self.queryset, self.request.GET, skede_orderable_fields)        
        return self.queryset

