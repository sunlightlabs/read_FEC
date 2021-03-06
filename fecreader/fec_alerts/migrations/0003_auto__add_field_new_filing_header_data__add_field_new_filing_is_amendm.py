# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'new_filing.header_data'
        
        ## south fucks up the hstore field. Just create it manually. 
        db.execute("alter table fec_alerts_new_filing ADD COLUMN header_data hstore")
        print "Ran custom sql to correctly create hstore"
        
        # Adding field 'new_filing.is_amendment'
        db.add_column(u'fec_alerts_new_filing', 'is_amendment',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'new_filing.amends_filing'
        db.add_column(u'fec_alerts_new_filing', 'amends_filing',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'new_filing.amendment_number'
        db.add_column(u'fec_alerts_new_filing', 'amendment_number',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'new_filing.is_superceded'
        db.add_column(u'fec_alerts_new_filing', 'is_superceded',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'new_filing.amended_by'
        db.add_column(u'fec_alerts_new_filing', 'amended_by',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'new_filing.covered_by_periodic_filing'
        db.add_column(u'fec_alerts_new_filing', 'covered_by_periodic_filing',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'new_filing.covered_by'
        db.add_column(u'fec_alerts_new_filing', 'covered_by',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'new_filing.header_data'
        db.delete_column(u'fec_alerts_new_filing', 'header_data')

        # Deleting field 'new_filing.is_amendment'
        db.delete_column(u'fec_alerts_new_filing', 'is_amendment')

        # Deleting field 'new_filing.amends_filing'
        db.delete_column(u'fec_alerts_new_filing', 'amends_filing')

        # Deleting field 'new_filing.amendment_number'
        db.delete_column(u'fec_alerts_new_filing', 'amendment_number')

        # Deleting field 'new_filing.is_superceded'
        db.delete_column(u'fec_alerts_new_filing', 'is_superceded')

        # Deleting field 'new_filing.amended_by'
        db.delete_column(u'fec_alerts_new_filing', 'amended_by')

        # Deleting field 'new_filing.covered_by_periodic_filing'
        db.delete_column(u'fec_alerts_new_filing', 'covered_by_periodic_filing')

        # Deleting field 'new_filing.covered_by'
        db.delete_column(u'fec_alerts_new_filing', 'covered_by')


## The models are possibly wrong. South was fucking up creating the hstore--just making sure it didn't try to create a default fixed it. Totally unclear why it wanted a default value when one wasn't specified in the model. 
    models = {
        u'fec_alerts.filing_scrape_time': {
            'Meta': {'object_name': 'Filing_Scrape_Time'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'fec_alerts.new_filing': {
            'Meta': {'ordering': "('-filing_number',)", 'object_name': 'new_filing'},
            'amended_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amendment_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amends_filing': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'body_rows_superceded': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'coh_end': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'coh_start': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'committee_designation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'committee_slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'committee_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'coverage_to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'covered_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'covered_by_periodic_filing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data_is_processed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filed_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'filing_is_downloaded': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'form_type': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'header_data': ('djorm_hstore.fields.DictionaryField', [], {'default': '{}', 'null': 'True'}),
            'header_is_processed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'ie_rows_processed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superceded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superpac': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'lines_present': ('djorm_hstore.fields.DictionaryField', [], {'default': '{}', 'null': 'True', 'db_index': 'True'}),
            'new_loans': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'previous_amendments_processed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'process_time': ('django.db.models.fields.DateTimeField', [], {}),
            'tot_ies': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'tot_raised': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'tot_spent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'})
        },
        u'fec_alerts.newcommittee': {
            'Meta': {'ordering': "('-date_filed',)", 'object_name': 'newCommittee'},
            'ctype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cycle': ('django.db.models.fields.CharField', [], {'default': "'2014'", 'max_length': '4'}),
            'date_filed': ('django.db.models.fields.DateField', [], {}),
            'fec_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9', 'blank': 'True'}),
            'has_overlay': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'fec_alerts.webk': {
            'Meta': {'object_name': 'WebK'},
            'add': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'can_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'can_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'can_loa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'can_loa_rep': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cas_on_han_beg_of_per': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cas_on_han_beg_of_yea': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cas_on_han_clo_of_per': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cas_on_han_clo_of_yea': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cit': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'com_des': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'com_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'com_nam': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'com_typ': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'coo_exp_par': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'cov_end_dat': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'cov_sta_dat': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'coverage_through_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'deb_owe_by_com': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'deb_owe_to_com': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'exe_leg_acc_dis_pre': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'exp_sub_lim': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'exp_sub_to_lim_pri_yea_pre': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'fec_ele_yea': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fed_can_com_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'fed_can_con_ref': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'fed_fun': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'fed_sha_of_joi_act': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'fil_fre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'fun_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ind_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ind_exp_mad': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ind_ite_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ind_ref': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ind_uni_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ite_con_exp_con_com': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ite_oth_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ite_oth_inc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ite_oth_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ite_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'lin_ima': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'loa_mad': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'loa_rep_rec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'net_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'net_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'non_all_fed_ele_act_par': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'non_fed_sha_of_joi_act': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'off_to_fun_exp_pre': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'off_to_leg_acc_exp_pre': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'off_to_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'org_tp': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'oth_com_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_com_ref': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_fed_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_loa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_loa_rep': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'oth_rec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'par_com_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'pol_par_com_ref': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'rep_typ': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sha_fed_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'sha_non_fed_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'sta': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'sub_con_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'sub_oth_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'sub_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_com_cos': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_con': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_con_ref': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_exp_sub_to_lim_pre': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_fed_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_fed_ele_act': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_fed_rec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_loa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_loa_rep': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_non_fed_tra': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_off_to_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_ope_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tot_rec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tra_fro_non_fed_acc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tra_fro_non_fed_lev_acc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tra_fro_oth_aut_com': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tra_to_oth_aut_com': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tre_nam': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'uni_con_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'uni_oth_dis': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'uni_oth_inc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'uni_oth_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'uni_ref_or_reb': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fec_alerts']