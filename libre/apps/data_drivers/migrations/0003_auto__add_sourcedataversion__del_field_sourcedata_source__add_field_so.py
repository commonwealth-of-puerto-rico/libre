# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourceDataVersion'
        db.create_table(u'data_drivers_sourcedataversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_drivers.Source'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 27, 0, 0))),
            ('checksum', self.gf('django.db.models.fields.TextField')()),
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceDataVersion'])

        # Deleting field 'SourceData.source'
        db.delete_column(u'data_drivers_sourcedata', 'source_id')

        # Adding field 'SourceData.source_data_version'
        db.add_column(u'data_drivers_sourcedata', 'source_data_version',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['data_drivers.SourceDataVersion']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'SourceDataVersion'
        db.delete_table(u'data_drivers_sourcedataversion')


        # User chose to not deal with backwards NULL issues for 'SourceData.source'
        raise RuntimeError("Cannot reverse this migration. 'SourceData.source' and its values cannot be restored.")
        # Deleting field 'SourceData.source_data_version'
        db.delete_column(u'data_drivers_sourcedata', 'source_data_version_id')


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
            'source_data_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_drivers.SourceDataVersion']"})
        },
        u'data_drivers.sourcedataversion': {
            'Meta': {'object_name': 'SourceDataVersion'},
            'checksum': ('django.db.models.fields.TextField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 27, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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