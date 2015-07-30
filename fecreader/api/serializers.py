
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay, Candidate_Overlay, DistrictWeekly, District
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
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present', 'form_name', 'skeda_url', 'spending_url', 'absolute_url', 'committee_url', 'process_time_formatted', 'is_superceded', 'cycle')


class COSerializer(serializers.HyperlinkedModelSerializer):
    display_type = serializers.Field(source='display_type')
    candidate_url = serializers.Field(source='candidate_url')
    candidate_office = serializers.Field(source='curated_candidate_office')
    candidate_name = serializers.Field(source='curated_candidate_name')
    committee_url = serializers.Field(source='get_absolute_url')  
    
    class Meta:
        model = Committee_Overlay
        fields=('fec_id', 'name', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype', 'candidate_office','candidate_name', 'candidate_url', 'display_type', 'committee_url', 'political_orientation')
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
        fields=('fec_id', 'name', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'ctype', 'total_indy_expenditures','ie_support_dems', 'ie_oppose_dems', 'ie_support_reps', 'ie_oppose_reps', 'political_orientation', 'political_orientation_verified', 'display_type', 'committee_url', 'get_filtered_ie_url', 'display_coh', 'display_coh_date', 'major_activity', 'cycle')
        #depth = 1



class DistrictSerializer(serializers.ModelSerializer):

    district_url = serializers.Field(source='get_absolute_url')  
    next_election = serializers.Field(source='next_election')

    class Meta:
        model = District
        fields=('id', 'district_url', 'cycle', 'state', 'office', 'office_district', 'term_class', 'incumbent_name', 'incumbent_party', 'next_election_date', 'next_election_code', 'next_election', 'open_seat', 'candidate_raised', 'candidate_spending', 'outside_spending', 'total_spending', 'rothenberg_rating_id', 'rothenberg_rating_text')
                
class MinimalDistrictSerializer(serializers.ModelSerializer):
    race_name = serializers.Field(source='__unicode__')
    class Meta:
        model = District
        fields=('race_name', 'state', 'office', 'office_district', 'term_class', 'id')



class CandidateSerializer(serializers.ModelSerializer):
    candidate_url = serializers.Field(source='get_absolute_url')  
    race_url = serializers.Field(source='get_race_url')
    ie_url = serializers.Field(source='get_filtered_ie_url')
    status = serializers.Field(source='show_candidate_status')  
    district = MinimalDistrictSerializer(source='district')
    

    class Meta:
        model = Candidate_Overlay
        fields=('name', 'fec_id', 'pcc', 'party', 'candidate_url', 'race_url', 'ie_url', 'is_incumbent', 'cycle', 'not_seeking_reelection', 'other_office_sought', 'other_fec_id', 'election_year', 'state', 'office', 'office_district', 'term_class', 'candidate_status', 'total_expenditures', 'expenditures_supporting', 'expenditures_opposing', 'total_receipts', 'total_contributions', 'total_disbursements', 'cash_on_hand', 'cash_on_hand_date', 'district', 'outstanding_loans', 'cand_is_gen_winner', 'status')



class DWSerializer(serializers.HyperlinkedModelSerializer):
    
    district = MinimalDistrictSerializer(source='district')
    
    class Meta:
        model = DistrictWeekly
        depth = 1
        fields=('start_date', 'end_date', 'cycle_week_number', 'outside_spending', 'district')


        
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
