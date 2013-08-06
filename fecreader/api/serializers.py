
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay
from rest_framework import serializers


class NFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = new_filing
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present')

class COSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Committee_Overlay
        fields=('fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype')