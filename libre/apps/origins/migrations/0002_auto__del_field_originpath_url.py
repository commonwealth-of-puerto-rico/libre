# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'OriginPath.url'
        db.delete_column(u'origins_originpath', 'url')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'OriginPath.url'
        raise RuntimeError("Cannot reverse this migration. 'OriginPath.url' and its values cannot be restored.")

    models = {
        u'origins.origin': {
            'Meta': {'object_name': 'Origin'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'origins.origindatabase': {
            'Meta': {'object_name': 'OriginDatabase', '_ormbases': [u'origins.Origin']},
            'db_backend': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'db_host': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'db_password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'db_port': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'db_query': ('django.db.models.fields.TextField', [], {}),
            'db_user': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'origins.originftpfile': {
            'Meta': {'object_name': 'OriginFTPFile'},
            'contained_file_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'origins.originpath': {
            'Meta': {'object_name': 'OriginPath', '_ormbases': [u'origins.Origin']},
            'contained_file_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'uncompress': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'origins.originrestapi': {
            'Meta': {'object_name': 'OriginRESTAPI'},
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'origins.originsoapwebservice': {
            'Meta': {'object_name': 'OriginSOAPWebService'},
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'origins.originuploadedfile': {
            'Meta': {'object_name': 'OriginUploadedFile', '_ormbases': [u'origins.Origin']},
            'contained_file_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'origins.originurlfile': {
            'Meta': {'object_name': 'OriginURLFile'},
            'contained_file_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'origin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['origins.Origin']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['origins']