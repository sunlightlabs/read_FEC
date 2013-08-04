
from fec_alerts.models import new_filing
from rest_framework import serializers


class NFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = new_filing
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present')
