# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Election'
        db.delete_table(u'summary_data_election')

        # Deleting model 'SubElection'
        db.delete_table(u'summary_data_subelection')

        # Deleting model 'Election_Candidate'
        db.delete_table(u'summary_data_election_candidate')

        # Deleting model 'SubElection_Candidate'
        db.delete_table(u'summary_data_subelection_candidate')


    def backwards(self, orm):
        # Adding model 'Election'
        db.create_table(u'summary_data_election', (
            ('open_seat', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('office_district', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('election_year', self.gf('django.db.models.fields.PositiveIntegerField')(blank=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.District'])),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('term_class', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('seat_isnew', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('election_code', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('incumbent_pty', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('incumbent_party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('incumbent_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('seat_redistricted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cycle', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
        ))
        db.send_create_signal(u'summary_data', ['Election'])

        # Adding model 'SubElection'
        db.create_table(u'summary_data_subelection', (
            ('parentElection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.Election'])),
            ('is_contested', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('election_voting_end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('subelection_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('election_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('primary_party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('election_other_description', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('election_voting_start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'summary_data', ['SubElection'])

        # Adding model 'Election_Candidate'
        db.create_table(u'summary_data_election_candidate', (
            ('is_sole_winner', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.Election'])),
            ('is_loser', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.Candidate_Overlay'])),
            ('advance_to_runoff', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('vote_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vote_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'summary_data', ['Election_Candidate'])

        # Adding model 'SubElection_Candidate'
        db.create_table(u'summary_data_subelection_candidate', (
            ('is_sole_winner', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.Election'])),
            ('is_loser', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['summary_data.Candidate_Overlay'])),
            ('advance_to_runoff', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('vote_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vote_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'summary_data', ['SubElection_Candidate'])


    models = {
        u'legislators.legislator': {
            'Meta': {'object_name': 'Legislator'},
            'bioguide': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'bioguide_previous': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cspan': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'govtrack': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'house_history': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icpsr': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '127', 'null': 'True', 'blank': 'True'}),
            'lis': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'official_full': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'opensecrets': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '127', 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'thomas': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'votesmart': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'wikipedia': ('django.db.models.fields.CharField', [], {'max_length': '127', 'null': 'True', 'blank': 'True'})
        },
        u'summary_data.authorized_candidate_committees': {
            'Meta': {'object_name': 'Authorized_Candidate_Committees'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'com_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'committee_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_pcc': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'summary_data.candidate_overlay': {
            'Meta': {'unique_together': "(('fec_id', 'cycle'),)", 'object_name': 'Candidate_Overlay'},
            'bio_blurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cand_cand_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_cand_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_ici': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'cand_is_gen_winner': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'candidate_status': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'cash_on_hand': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cash_on_hand_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'crp_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'curated_election_year': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['summary_data.District']", 'null': 'True'}),
            'election_year': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'electioneering': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'has_contributions': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general_candidate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_incumbent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_minor_candidate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'not_seeking_reelection': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'office_district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'other_fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'other_office_sought': ('django.db.models.fields.CharField', [], {'max_length': '127', 'null': 'True', 'blank': 'True'}),
            'outstanding_loans': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'pcc': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'pty': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'term_class': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_contributions': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_disbursements': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_expenditures': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_receipts': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_unitemized': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'transparency_id': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'transparencydata_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'null': 'True'})
        },
        u'summary_data.candidate_time_summary': {
            'Meta': {'object_name': 'Candidate_Time_Summary'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'cash_on_hand_end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'coverage_through_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'outstanding_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_disburse': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_ite_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_non_ite_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'})
        },
        u'summary_data.committee_overlay': {
            'Meta': {'ordering': "('-total_indy_expenditures',)", 'unique_together': "(('cycle', 'fec_id'),)", 'object_name': 'Committee_Overlay'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'candidate_office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'cash_on_hand': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cash_on_hand_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'connected_org_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ctype': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'curated_candidate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_candidate'", 'null': 'True', 'to': u"orm['summary_data.Candidate_Overlay']"}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'filing_frequency': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'has_contributions': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'has_coordinated_expenditures': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'has_electioneering': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'has_independent_expenditures': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ie_oppose_dems': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_oppose_reps': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_support_dems': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_support_reps': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'is_dirty': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'is_hybrid': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_noncommittee': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_paper_filer': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_superpac': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'org_status': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'outstanding_loans': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'political_orientation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'political_orientation_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'term_class': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_contributions': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_coordinated_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_disbursements': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_electioneering': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_indy_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_presidential_indy_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_receipts': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_unitemized': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'treasurer': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'})
        },
        u'summary_data.committee_time_summary': {
            'Meta': {'object_name': 'Committee_Time_Summary'},
            'cash_on_hand_end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'com_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'com_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'coo_exp_par': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'coverage_through_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'electioneering_made': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ind_exp_mad': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'new_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'outstanding_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_disburse': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_ite_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_non_ite_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'tot_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'})
        },
        u'summary_data.district': {
            'Meta': {'ordering': "['state', '-office', 'office_district']", 'object_name': 'District'},
            'altered_by_2010_redistricting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_raised': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'candidate_spending': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'coordinated_spending': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'dem_frac_historical': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'district_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'election_year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'electioneering_spending': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incumbent_legislator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legislators.Legislator']", 'null': 'True'}),
            'incumbent_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'incumbent_party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'incumbent_pty': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'next_election_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'next_election_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'office_district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'open_seat': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'outside_spending': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'rep_frac_historical': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rothenberg_rating_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'rothenberg_rating_text': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True'}),
            'rothenberg_update_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'special_election_scheduled': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'term_class': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_spending': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        u'summary_data.filing_gap': {
            'Meta': {'object_name': 'Filing_Gap'},
            'committee_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'gap_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'gap_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'summary_data.incumbent': {
            'Meta': {'object_name': 'Incumbent'},
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_incumbent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'office_district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'})
        },
        u'summary_data.pac_candidate': {
            'Meta': {'ordering': "('-total_ind_exp',)", 'object_name': 'Pac_Candidate'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['summary_data.Candidate_Overlay']"}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['summary_data.Committee_Overlay']"}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_oppose': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'total_coord_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        u'summary_data.state_aggregate': {
            'Meta': {'object_name': 'State_Aggregate'},
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'expenditures_opposing_house': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing_president': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing_senate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_house': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_president': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_senate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recent_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'recent_pres_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'total_coord': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_house_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_pres_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_senate_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        u'summary_data.update_time': {
            'Meta': {'object_name': 'Update_Time'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['summary_data']