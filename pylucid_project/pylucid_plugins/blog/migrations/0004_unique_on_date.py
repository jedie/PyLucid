# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    no_dry_run = True # Data migrations shouldn't be dry-run

    def forwards(self, orm):
        # Adding field 'BlogEntryContent.date'
        db.add_column('blog_blogentrycontent', 'url_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now),
                      keep_default=False)

        print "\tDo datamigration of blog entries:",
        for instance in orm.BlogEntryContent.objects.all():
            print instance.pk,
            instance.url_date = instance.createtime
            instance.save()
        print

        print "\tMake all blog entries unique:"
        pks = orm.BlogEntryContent.objects.all().order_by('createtime', 'lastupdatetime').values_list("pk", flat=True)
        for pk in pks:
            instance = orm.BlogEntryContent.objects.get(pk=pk)
            # Test only if slug is unique and change slug + headline if not
            queryset = orm.BlogEntryContent.objects.all().order_by('createtime', 'lastupdatetime').filter(
                language = instance.language,
                url_date = instance.url_date,
                slug = instance.slug,
            )
            queryset = queryset.exclude(pk=instance.pk)
            for no, instance2 in enumerate(queryset, 2):
                print "\t old:", instance2.pk, instance2.slug, instance2.headline
                suffix = "%s" % no
                instance2.slug += suffix
                instance2.headline += suffix
                instance2.save()
                print "\t new:", instance2.pk, instance2.slug, instance2.headline
        print

        # Adding unique constraint on 'BlogEntryContent', fields ['url_date', 'headline', 'language']
        db.create_unique('blog_blogentrycontent', ['url_date', 'slug', 'language_id'])

        # Adding unique constraint on 'BlogEntryContent', fields ['url_date', 'headline', 'language']
        db.create_unique('blog_blogentrycontent', ['url_date', 'headline', 'language_id'])  


    def backwards(self, orm):
        # Removing unique constraint on 'BlogEntryContent', fields ['url_date', 'headline', 'language']
        db.delete_unique('blog_blogentrycontent', ['url_date', 'slug', 'language_id'])

        # Removing unique constraint on 'BlogEntryContent', fields ['url_date', 'headline', 'language']
        db.delete_unique('blog_blogentrycontent', ['url_date', 'headline', 'language_id'])

        # Deleting field 'BlogEntryContent.date'
        db.delete_column('blog_blogentrycontent', 'url_date')


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
            'Meta': {'object_name': 'BlogEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'})
        },
        'blog.blogentrycontent': {
            'Meta': {'ordering': "('-createtime', '-lastupdatetime')", 'unique_together': "(('language', 'url_date', 'headline'), ('language', 'url_date', 'headline'))", 'object_name': 'BlogEntryContent'},
            'content': ('pylucid_project.apps.pylucid.fields.MarkupContentModelField', [], {'blank': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentrycontent_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'url_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blog.BlogEntry']"}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']"}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blogentrycontent_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markup': ('pylucid_project.apps.pylucid.fields.MarkupModelField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'}),
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
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'permitViewGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language_permitViewGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['blog']