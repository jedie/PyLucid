# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BlogEntry'
        db.create_table('blog_blogentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blogentry_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blogentry_lastupdateby', null=True, to=orm['auth.User'])),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('pylucid_project.apps.pylucid.fields.MarkupContentModelField')()),
            ('markup', self.gf('pylucid_project.apps.pylucid.fields.MarkupModelField')()),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.Language'])),
            ('tags', self.gf('django_tools.tagging_addon.fields.jQueryTagModelField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('blog', ['BlogEntry'])

        # Adding M2M table for field sites on 'BlogEntry'
        db.create_table('blog_blogentry_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blogentry', models.ForeignKey(orm['blog.blogentry'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('blog_blogentry_sites', ['blogentry_id', 'site_id'])


    def backwards(self, orm):
        
        # Deleting model 'BlogEntry'
        db.delete_table('blog_blogentry')

        # Removing M2M table for field sites on 'BlogEntry'
        db.delete_table('blog_blogentry_sites')


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
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
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
