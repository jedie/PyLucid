# coding: utf-8

import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for template in orm['dbtemplates.template'].objects.all():
            content = template.content
            content = content.replace(u"{{ Django_media_prefix }}", u"{{ STATIC_URL }}admin/")
            content = content.replace(u"{{ PyLucid_media_url }}", u"{{ STATIC_URL }}PyLucid/")
            if content != template.content:
                print " * Update template: %r" % template.name
                template.content = content
                template.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        for template in orm['dbtemplates.template'].objects.all():
            content = template.content
            content = content.replace(u"{{ STATIC_URL }}admin/", u"{{ Django_media_prefix }}")
            content = content.replace(u"{{ STATIC_URL }}PyLucid/", u"{{ PyLucid_media_url }}")
            if content != template.content:
                print " * Revered template: %r" % template.name
                template.save()

    models = {
        'dbtemplates.template': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Template', 'db_table': "'django_template'"},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['dbtemplates']
    symmetrical = True
