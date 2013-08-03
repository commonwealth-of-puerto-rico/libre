# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Icon'
        db.create_table(u'icons_icon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=48)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=48, blank=True)),
            ('icon_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'icons', ['Icon'])


    def backwards(self, orm):
        # Deleting model 'Icon'
        db.delete_table(u'icons_icon')


    models = {
        u'icons.icon': {
            'Meta': {'object_name': 'Icon'},
            'icon_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '48'})
        }
    }

    complete_apps = ['icons']