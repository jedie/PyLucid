# encoding: utf-8

"""
    Split the blog model into two models with
    language depend and independent informations.

    see also:
    
    https://github.com/jedie/PyLucid/issues/28
    https://github.com/jedie/PyLucid/issues/64
    
    First we create the new table and do a data migration.
    In second step we remove all unused columns from BlogEntry model.
"""

import datetime

from south.db import db
from south.v2 import SchemaMigration

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class Migration(SchemaMigration):

    no_dry_run = True # Data migrations shouldn't be dry-run

    def forwards(self, orm):
        # Adding model 'BlogEntryContent'
        db.create_table('blog_blogentrycontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blogentrycontent_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blogentrycontent_lastupdateby', null=True, to=orm['auth.User'])),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blog.BlogEntry'])),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=255, blank=True)),
            ('content', self.gf('pylucid_project.apps.pylucid.fields.MarkupContentModelField')()),
            ('markup', self.gf('pylucid_project.apps.pylucid.fields.MarkupModelField')()),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.Language'])),
            ('tags', self.gf('django_tools.tagging_addon.fields.jQueryTagModelField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('blog', ['BlogEntryContent'])

        print "\tDo datamigration of blog entries:",
        for entry in orm.BlogEntry.objects.all():
            print entry.pk,
            new_entry = orm.BlogEntryContent.objects.create(
                entry=entry,
                createby=entry.createby,
                lastupdateby=entry.lastupdateby,
                headline=entry.headline,
                slug=slugify(entry.headline),
                content=entry.content,
                markup=entry.markup,
                language=entry.language,
                tags=entry.tags,
                is_public=entry.is_public,
            )

            # Temorary disable auto new function
            # see: http://stackoverflow.com/questions/7499767/temporarily-disable-auto-now-auto-now-add
            for field in new_entry._meta.local_fields:
                if field.name == "lastupdatetime":
                    field.auto_now = False
                elif field.name == "createtime":
                    field.auto_now_add = False

            new_entry.createtime = entry.createtime
            new_entry.lastupdatetime = entry.lastupdatetime
            new_entry.save()

            for field in new_entry._meta.local_fields:
                if field.name == "lastupdatetime":
                    field.auto_now = True
                elif field.name == "createtime":
                    field.auto_now_add = True
        print "done."


    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blog.blogentry': {
            'Meta': {'ordering': "('-createtime', '-lastupdatetime')", 'object_name': 'BlogEntry'},
            'content': ('pylucid_project.apps.pylucid.fields.MarkupContentModelField', [], {}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentry_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']"}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentry_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'markup': ('pylucid_project.apps.pylucid.fields.MarkupModelField', [], {}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': [settings.SITE_ID], 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'tags': ('django_tools.tagging_addon.fields.jQueryTagModelField', [], {})
        },
        'blog.blogentrycontent': {
            'Meta': {'ordering': "('-createtime', '-lastupdatetime')", 'object_name': 'BlogEntryContent'},
            'content': ('pylucid_project.apps.pylucid.fields.MarkupContentModelField', [], {}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentrycontent_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blog.BlogEntry']"}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']"}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentrycontent_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'markup': ('pylucid_project.apps.pylucid.fields.MarkupModelField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'tags': ('django_tools.tagging_addon.fields.jQueryTagModelField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pylucid.language': {
            'Meta': {'ordering': "('code',)", 'object_name': 'Language'},
            'code': ('django_tools.fields.language_code.LanguageCodeModelField', [], {'unique': 'True', 'max_length': '10'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'permitViewGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language_permitViewGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': [settings.SITE_ID], 'to': "orm['sites.Site']", 'symmetrical': 'False'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['blog']
