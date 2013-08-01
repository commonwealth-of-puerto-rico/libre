# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DatabaseConnection'
        db.create_table(u'db_drivers_databaseconnection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('backend', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'db_drivers', ['DatabaseConnection'])


    def backwards(self, orm):
        # Deleting model 'DatabaseConnection'
        db.delete_table(u'db_drivers_databaseconnection')


    models = {
        u'db_drivers.databaseconnection': {
            'Meta': {'ordering': "['name']", 'object_name': 'DatabaseConnection'},
            'backend': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        }
    }

    complete_apps = ['db_drivers']