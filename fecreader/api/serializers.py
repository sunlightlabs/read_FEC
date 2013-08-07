
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from rest_framework import serializers


class NFSerializer(serializers.HyperlinkedModelSerializer):
    form_name = serializers.Field(source='get_form_name')
    process_time_formatted = serializers.Field(source='process_time_formatted')
    skeda_url = serializers.Field(source='get_skeda_url') 
    skedb_url = serializers.Field(source='get_skedb_url') 
    absolute_url = serializers.Field(source='get_absolute_url') 
    committee_url = serializers.Field(source='get_committee_url')  
    
    class Meta:
        model = new_filing
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present', 'form_name', 'skeda_url', 'skedb_url', 'absolute_url', 'committee_url', 'process_time_formatted')

class COSerializer(serializers.HyperlinkedModelSerializer):
    display_type = serializers.Field(source='display_type')
    candidate_url = serializers.Field(source='candidate_url')
    candidate_office = serializers.Field(source='curated_candidate_office')
    candidate_name = serializers.Field(source='curated_candidate_name')
    committee_url = serializers.Field(source='get_absolute_url')  
    
    
    class Meta:
        model = Committee_Overlay
        fields=('fec_id', 'name', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype', 'candidate_office','candidate_name', 'candidate_url', 'display_type', 'committee_url')
        #depth = 1