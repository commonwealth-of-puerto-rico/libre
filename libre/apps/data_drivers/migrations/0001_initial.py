# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table(u'data_drivers_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=48, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['Source'])

        # Adding model 'SourceWS'
        db.create_table(u'data_drivers_sourcews', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('wsdl_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('endpoint', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceWS'])

        # Adding model 'WSArgument'
        db.create_table(u'data_drivers_wsargument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_ws', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_drivers.SourceWS'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['WSArgument'])

        # Adding model 'WSResultField'
        db.create_table(u'data_drivers_wsresultfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_ws', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_drivers.SourceWS'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['WSResultField'])

        # Adding model 'SourceCSV'
        db.create_table(u'data_drivers_sourcecsv', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('import_rows', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('delimiter', self.gf('django.db.models.fields.CharField')(default=',', max_length=1, blank=True)),
            ('quote_character', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceCSV'])

        # Adding model 'SourceFixedWidth'
        db.create_table(u'data_drivers_sourcefixedwidth', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('import_rows', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceFixedWidth'])

        # Adding model 'SourceSpreadsheet'
        db.create_table(u'data_drivers_sourcespreadsheet', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('import_rows', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sheet', self.gf('django.db.models.fields.CharField')(default='0', max_length=32)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceSpreadsheet'])

        # Adding model 'SourceShape'
        db.create_table(u'data_drivers_sourceshape', (
            (u'source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_drivers.Source'], unique=True, primary_key=True)),
            ('limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('path', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('popup_template', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceShape'])

        # Adding model 'SourceDataVersion'
        db.create_table(u'data_drivers_sourcedataversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='versions', to=orm['data_drivers.Source'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 7, 16, 0, 0))),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('checksum', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('metadata', self.gf('django.db.models.fields.TextField')(default={}, blank=True)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceDataVersion'])

        # Adding unique constraint on 'SourceDataVersion', fields ['source', 'datetime']
        db.create_unique(u'data_drivers_sourcedataversion', ['source_id', 'datetime'])

        # Adding unique constraint on 'SourceDataVersion', fields ['source', 'timestamp']
        db.create_unique(u'data_drivers_sourcedataversion', ['source_id', 'timestamp'])

        # Adding unique constraint on 'SourceDataVersion', fields ['source', 'checksum']
        db.create_unique(u'data_drivers_sourcedataversion', ['source_id', 'checksum'])

        # Adding model 'SourceData'
        db.create_table(u'data_drivers_sourcedata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_data_version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data', to=orm['data_drivers.SourceDataVersion'])),
            ('row', self.gf('django.db.models.fields.TextField')(default={})),
            ('row_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'data_drivers', ['SourceData'])

        # Adding model 'CSVColumn'
        db.create_table(u'data_drivers_csvcolumn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='columns', to=orm['data_drivers.SourceCSV'])),
            ('data_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'data_drivers', ['CSVColumn'])

        # Adding model 'FixedWidthColumn'
        db.create_table(u'data_drivers_fixedwidthcolumn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='columns', to=orm['data_drivers.SourceFixedWidth'])),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'data_drivers', ['FixedWidthColumn'])

        # Adding model 'SpreadsheetColumn'
        db.create_table(u'data_drivers_spreadsheetcolumn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='columns', to=orm['data_drivers.SourceSpreadsheet'])),
        ))
        db.send_create_signal(u'data_drivers', ['SpreadsheetColumn'])


    def backwards(self, orm):
        # Removing unique constraint on 'SourceDataVersion', fields ['source', 'checksum']
        db.delete_unique(u'data_drivers_sourcedataversion', ['source_id', 'checksum'])

        # Removing unique constraint on 'SourceDataVersion', fields ['source', 'timestamp']
        db.delete_unique(u'data_drivers_sourcedataversion', ['source_id', 'timestamp'])

        # Removing unique constraint on 'SourceDataVersion', fields ['source', 'datetime']
        db.delete_unique(u'data_drivers_sourcedataversion', ['source_id', 'datetime'])

        # Deleting model 'Source'
        db.delete_table(u'data_drivers_source')

        # Deleting model 'SourceWS'
        db.delete_table(u'data_drivers_sourcews')

        # Deleting model 'WSArgument'
        db.delete_table(u'data_drivers_wsargument')

        # Deleting model 'WSResultField'
        db.delete_table(u'data_drivers_wsresultfield')

        # Deleting model 'SourceCSV'
        db.delete_table(u'data_drivers_sourcecsv')

        # Deleting model 'SourceFixedWidth'
        db.delete_table(u'data_drivers_sourcefixedwidth')

        # Deleting model 'SourceSpreadsheet'
        db.delete_table(u'data_drivers_sourcespreadsheet')

        # Deleting model 'SourceShape'
        db.delete_table(u'data_drivers_sourceshape')

        # Deleting model 'SourceDataVersion'
        db.delete_table(u'data_drivers_sourcedataversion')

        # Deleting model 'SourceData'
        db.delete_table(u'data_drivers_sourcedata')

        # Deleting model 'CSVColumn'
        db.delete_table(u'data_drivers_csvcolumn')

        # Deleting model 'FixedWidthColumn'
        db.delete_table(u'data_drivers_fixedwidthcolumn')

        # Deleting model 'SpreadsheetColumn'
        db.delete_table(u'data_drivers_spreadsheetcolumn')


    models = {
        u'data_drivers.csvcolumn': {
            'Meta': {'object_name': 'CSVColumn'},
            'data_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'columns'", 'to': u"orm['data_drivers.SourceCSV']"})
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
        u'data_drivers.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
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
        u'data_drivers.sourcedataversion': {
            'Meta': {'unique_together': "(('source', 'datetime'), ('source', 'timestamp'), ('source', 'checksum'))", 'object_name': 'SourceDataVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 7, 16, 0, 0)'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
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
        }
    }

    complete_apps = ['data_drivers']