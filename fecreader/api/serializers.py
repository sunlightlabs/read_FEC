
from fec_alerts.models import new_filing
from rest_framework import serializers


class NFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = new_filing
        fields = ('fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'tot_raised')
