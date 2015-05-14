# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HouseRace'
        db.create_table(u'rothenberg_houserace', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('district', self.gf('django.db.models.fields.IntegerField')()),
            ('rating_id', self.gf('django.db.models.fields.IntegerField')()),
            ('rating_label', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('incumbent', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rothenberg', ['HouseRace'])

        # Adding unique constraint on 'HouseRace', fields ['state', 'district']
        db.create_unique(u'rothenberg_houserace', ['state', 'district'])

        # Adding model 'SenateRace'
        db.create_table(u'rothenberg_senaterace', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('seat_class', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('rating_id', self.gf('django.db.models.fields.IntegerField')()),
            ('rating_segment', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('rating_label', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('incumbent', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rothenberg', ['SenateRace'])

        # Adding unique constraint on 'SenateRace', fields ['state', 'seat_class']
        db.create_unique(u'rothenberg_senaterace', ['state', 'seat_class'])


    def backwards(self, orm):
        # Removing unique constraint on 'SenateRace', fields ['state', 'seat_class']
        db.delete_unique(u'rothenberg_senaterace', ['state', 'seat_class'])

        # Removing unique constraint on 'HouseRace', fields ['state', 'district']
        db.delete_unique(u'rothenberg_houserace', ['state', 'district'])

        # Deleting model 'HouseRace'
        db.delete_table(u'rothenberg_houserace')

        # Deleting model 'SenateRace'
        db.delete_table(u'rothenberg_senaterace')


    models = {
        u'rothenberg.houserace': {
            'Meta': {'unique_together': "(('state', 'district'),)", 'object_name': 'HouseRace'},
            'district': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incumbent': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'rating_id': ('django.db.models.fields.IntegerField', [], {}),
            'rating_label': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'rothenberg.senaterace': {
            'Meta': {'unique_together': "(('state', 'seat_class'),)", 'object_name': 'SenateRace'},
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