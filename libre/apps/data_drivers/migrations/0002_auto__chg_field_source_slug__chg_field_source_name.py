# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Source.slug'
        db.alter_column(u'data_drivers_source', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=48))

        # Changing field 'Source.name'
        db.alter_column(u'data_drivers_source', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

    def backwards(self, orm):

        # Changing field 'Source.slug'
        db.alter_column(u'data_drivers_source', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=32))

        # Changing field 'Source.name'
        db.alter_column(u'data_drivers_source', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

    models = {
        u'data_drivers.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '48', 'blank': 'True'})
        },
        u'data_drivers.sourcedata': {
            'Meta': {'object_name': 'SourceData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_drivers.Source']"})
        },
        u'data_drivers.sourcespreadsheet': {
            'Meta': {'object_name': 'SourceSpreadsheet', '_ormbases': [u'data_drivers.Source']},
            'column_names': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'first_row_names': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sheet': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['data_drivers']