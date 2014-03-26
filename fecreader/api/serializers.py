
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay, Candidate_Overlay
from formdata.models import SkedE
from rest_framework import serializers


class NFSerializer(serializers.HyperlinkedModelSerializer):
    form_name = serializers.Field(source='get_form_name')
    process_time_formatted = serializers.Field(source='process_time_formatted')
    skeda_url = serializers.Field(source='get_skeda_url') 
    spending_url = serializers.Field(source='get_spending_url') 
    absolute_url = serializers.Field(source='get_absolute_url') 
    committee_url = serializers.Field(source='get_committee_url')  
    
    class Meta:
        model = new_filing
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present', 'form_name', 'skeda_url', 'spending_url', 'absolute_url', 'committee_url', 'process_time_formatted', 'is_superceded')


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

class OSSerializer(serializers.HyperlinkedModelSerializer):
    display_type = serializers.Field(source='display_type')
    committee_url = serializers.Field(source='get_absolute_url')  
    get_filtered_ie_url = serializers.Field(source='get_filtered_ie_url')
    display_coh_date =  serializers.Field(source='display_coh_date')
    display_coh =  serializers.Field(source='display_coh')
    major_activity = serializers.Field(source='major_activity')

    class Meta:
        model = Committee_Overlay
        fields=('fec_id', 'name', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'ctype', 'total_indy_expenditures','ie_support_dems', 'ie_oppose_dems', 'ie_support_reps', 'ie_oppose_reps', 'political_orientation', 'political_orientation_verified', 'display_type', 'committee_url', 'get_filtered_ie_url', 'display_coh', 'display_coh_date', 'major_activity')
        #depth = 1
        
class SkedESerializer(serializers.ModelSerializer):
    payee_name_simplified = serializers.Field(source='payee_name_simplified')
    candidate_url = serializers.Field(source='get_candidate_url')
    committee_url = serializers.Field(source='get_committee_url')
    short_office = serializers.Field(source='short_office')
    candidate_name = serializers.Field(source='candidate_name_raw')
    race_url = serializers.Field(source='get_race_url')
    
    class Meta:
        model = SkedE
        fields=('form_type', 'superceded_by_amendment', 'candidate_id_checked', 'candidate_name', 'candidate_party_checked', 'candidate_office_checked', 'candidate_state_checked', 'candidate_district_checked', 'support_oppose_checked', 'committee_name', 'transaction_id', 'payee_organization_name', 'payee_street_1', 'payee_street_2', 'payee_city', 'payee_state', 'payee_zip', 'payee_name_simplified', 'election_code', 'election_other_description', 'expenditure_date_formatted', 'expenditure_amount', 'expenditure_purpose_code', 'expenditure_purpose_descrip', 'date_signed_formatted', 'memo_code', 'memo_text_description', 'filer_committee_id_number', 'district_checked', 'race_url', 'committee_url', 'candidate_url', 'short_office')
