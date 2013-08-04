# Create your views here.
from fec_alerts.models import new_filing
from rest_framework import viewsets
from rest_framework import generics
from api.serializers import NFSerializer
import django_filters

class NFFilter(django_filters.FilterSet):
    
    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='tot_raised', lookup_type='gte')
    max_raised = django_filters.NumberFilter(name='tot_raised', lookup_type='lte')
    
    filed_before = django_filters.DateFilter(name='filed_date', lookup_type='lte') 
    filed_after = django_filters.DateFilter(name='filed_date', lookup_type='gte') 
    

    class Meta:
        model = new_filing
        fields = ['fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present']
        
#generics.ListAPIView
# viewsets.ModelViewSet
# viewsets.ReadOnlyModelViewSet


class NFViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = new_filing.objects.all()
    serializer_class = NFSerializer
    filter_class = NFFilter
    paginate_by = 100
    
# date => http://localhost:8000/api/new_filing/?filed_date=2013-07-29
