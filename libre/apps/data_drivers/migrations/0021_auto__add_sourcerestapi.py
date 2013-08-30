# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourceRESTAPI'
        db.create_table(u'data_drivers_sourcerestapi', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceRESTAPI'])


    def backwards(self, orm):
        # Deleting model 'SourceRESTAPI'
        db.delete_table(u'data_drivers_sourcerestapi')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        u'data_drivers.leafletmarker': {
            'Meta': {'ordering': "['label', 'slug']", 'object_name': 'LeafletMarker'},
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'leafletmarker-icon'", 'to': u"orm['icons.Icon']"}),
            'icon_anchor_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'icon_anchor_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'}),
            'popup_anchor_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'popup_anchor_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shadow': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'leafletmarker-shadow'", 'null': 'True', 'to': u"orm['icons.Icon']"}),
            'shadow_anchor_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shadow_anchor_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'})
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
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'Source'},
            'allowed_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '48', 'blank': 'True'})
        },
        u'data_drivers.sourcecsv': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceCSV', '_ormbases': [u'data_drivers.Source']},
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
            'row': ('picklefield.fields.PickledObjectField', [], {}),
            'row_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'source_data_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': u"orm['data_drivers.SourceDataVersion']"})
        },
        u'data_drivers.sourcedatabase': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceDatabase', '_ormbases': [u'data_drivers.Source']},
            'database_connection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['db_drivers.DatabaseConnection']"}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'data_drivers.sourcedataversion': {
            'Meta': {'unique_together': "(('source', 'datetime'), ('source', 'timestamp'), ('source', 'checksum'))", 'object_name': 'SourceDataVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 29, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('picklefield.fields.PickledObjectField', [], {'blank': 'True'}),
            'ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['data_drivers.Source']"}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'data_drivers.sourcefixedwidth': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceFixedWidth', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'import_rows': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcerestapi': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceRESTAPI', '_ormbases': [u'data_drivers.Source']},
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'data_drivers.sourceshape': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceShape', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'marker_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'markers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['data_drivers.LeafletMarker']", 'null': 'True', 'blank': 'True'}),
            'new_projection': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'popup_template': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'template_header': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcespreadsheet': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceSpreadsheet', '_ormbases': [u'data_drivers.Source']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'import_rows': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sheet': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32'}),
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_drivers.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'data_drivers.sourcews': {
            'Meta': {'ordering': "['name', 'slug']", 'object_name': 'SourceWS', '_ormbases': [u'data_drivers.Source']},
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
        },
        u'icons.icon': {
            'Meta': {'ordering': "['label', 'name']", 'object_name': 'Icon'},
            'icon_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '48'})
        }
    }

    complete_apps = ['data_drivers']