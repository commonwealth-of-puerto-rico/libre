# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ShapefileColumn.new_name'
        db.add_column(u'data_drivers_shapefilecolumn', 'new_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ShapefileColumn.new_name'
        db.delete_column(u'data_drivers_shapefilecolumn', 'new_name')


    models = {
        u'data_drivers.csvcolumn': {
            'Meta': {'object_name': 'CSVColumn'},
            'data_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_regex': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skip_regex': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceCSV']"})
        },
        u'data_drivers.databaseresultcolumn': {
            'Meta': {'object_name': 'DatabaseResultColumn'},
            'data_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceDatabase']"})
        },
        u'data_drivers.fixedwidthcolumn': {
            'Meta': {'object_name': 'FixedWidthColumn'},
            'data_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceFixedWidth']"})
        },
        u'data_drivers.shapefilecolumn': {
            'Meta': {'object_name': 'ShapefileColumn'},
            'data_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'new_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceShape']"})
        },
        u'data_drivers.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '48', 'blank': 'True'})
        },
        u'data_drivers.sourcecsv': {
            'Meta': {'object_name': 'SourceCSV', '_ormbases': [u'data_drivers.Source']},
            'delimiter': ('django.db.models.fields.CharField', [], {'default': "','", 'max_length': '1', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'import_rows': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'quote_character': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcedata': {
            'Meta': {'object_name': 'SourceData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.TextField', [], {'default': '{}'}),
            'row_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'source_data_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': u"orm['data_drivers.SourceDataVersion']"})
        },
        u'data_drivers.sourcedatabase': {
            'Meta': {'object_name': 'SourceDatabase', '_ormbases': [u'data_drivers.Source']},
            'database_connection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['db_drivers.DatabaseConnection']"}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'data_drivers.sourcedataversion': {
            'Meta': {'unique_together': "(('source', 'datetime'), ('source', 'timestamp'), ('source', 'checksum'))", 'object_name': 'SourceDataVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'default': '{}', 'blank': 'True'}),
            'ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['data_drivers.Source']"}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'data_drivers.sourcefixedwidth': {
            'Meta': {'object_name': 'SourceFixedWidth', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'import_rows': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourceshape': {
            'Meta': {'object_name': 'SourceShape', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'new_projection': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'popup_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcespreadsheet': {
            'Meta': {'object_name': 'SourceSpreadsheet', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'import_rows': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sheet': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcews': {
            'Meta': {'object_name': 'SourceWS', '_ormbases': [u'data_drivers.Source']},
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'wsdl_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'data_drivers.spreadsheetcolumn': {
            'Meta': {'object_name': 'SpreadsheetColumn'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_regex': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skip_regex': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceSpreadsheet']"})
        },
        u'data_drivers.wsargument': {
            'Meta': {'object_name': 'WSArgument'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'source_ws': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_drivers.SourceWS']"})
        },
        u'data_drivers.wsresultfield': {
            'Meta': {'object_name': 'WSResultField'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'source_ws': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_drivers.SourceWS']"})
        },
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

    complete_apps = ['data_drivers']
