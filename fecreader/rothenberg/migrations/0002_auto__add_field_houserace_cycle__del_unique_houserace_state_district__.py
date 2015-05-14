# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SenateRace', fields ['state', 'seat_class']
        db.delete_unique(u'rothenberg_senaterace', ['state', 'seat_class'])

        # Removing unique constraint on 'HouseRace', fields ['state', 'district']
        db.delete_unique(u'rothenberg_houserace', ['state', 'district'])

        # Adding field 'HouseRace.cycle'
        db.add_column(u'rothenberg_houserace', 'cycle',
                      self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'HouseRace', fields ['state', 'district', 'cycle']
        db.create_unique(u'rothenberg_houserace', ['state', 'district', 'cycle'])

        # Adding field 'SenateRace.cycle'
        db.add_column(u'rothenberg_senaterace', 'cycle',
                      self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'SenateRace', fields ['state', 'seat_class', 'cycle']
        db.create_unique(u'rothenberg_senaterace', ['state', 'seat_class', 'cycle'])


    def backwards(self, orm):
        # Removing unique constraint on 'SenateRace', fields ['state', 'seat_class', 'cycle']
        db.delete_unique(u'rothenberg_senaterace', ['state', 'seat_class', 'cycle'])

        # Removing unique constraint on 'HouseRace', fields ['state', 'district', 'cycle']
        db.delete_unique(u'rothenberg_houserace', ['state', 'district', 'cycle'])

        # Deleting field 'HouseRace.cycle'
        db.delete_column(u'rothenberg_houserace', 'cycle')

        # Adding unique constraint on 'HouseRace', fields ['state', 'district']
        db.create_unique(u'rothenberg_houserace', ['state', 'district'])

        # Deleting field 'SenateRace.cycle'
        db.delete_column(u'rothenberg_senaterace', 'cycle')

        # Adding unique constraint on 'SenateRace', fields ['state', 'seat_class']
        db.create_unique(u'rothenberg_senaterace', ['state', 'seat_class'])


    models = {
        u'rothenberg.houserace': {
            'Meta': {'unique_together': "(('state', 'district', 'cycle'),)", 'object_name': 'HouseRace'},
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incumbent': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'rating_id': ('django.db.models.fields.IntegerField', [], {}),
            'rating_label': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'rothenberg.senaterace': {
            'Meta': {'unique_together': "(('state', 'seat_class', 'cycle'),)", 'object_name': 'SenateRace'},
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incumbent': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'rating_id': ('django.db.models.fields.IntegerField', [], {}),
            'rating_label': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'rating_segment': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'seat_class': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rothenberg']