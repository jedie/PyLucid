# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'UserProfile.sha_login_salt'
        db.alter_column('pylucid_userprofile', 'sha_login_salt', self.gf('django.db.models.fields.CharField')(max_length=12))

    def backwards(self, orm):
        # Changing field 'UserProfile.sha_login_salt'
        db.alter_column('pylucid_userprofile', 'sha_login_salt', self.gf('django.db.models.fields.CharField')(max_length=5))

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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pylucid.banentry': {
            'Meta': {'ordering': "('-createtime',)", 'object_name': 'BanEntry'},
            'createtime': ('django.db.models.fields.DateTimeField', [], {}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'primary_key': 'True'})
        },
        'pylucid.color': {
            'Meta': {'ordering': "('colorscheme', 'name')", 'unique_together': "(('colorscheme', 'name'),)", 'object_name': 'Color'},
            'colorscheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.ColorScheme']"}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'color_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'color_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'value': ('pylucid_project.apps.pylucid.fields.ColorValueField', [], {'max_length': '6'})
        },
        'pylucid.colorscheme': {
            'Meta': {'object_name': 'ColorScheme'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'colorscheme_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'colorscheme_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pylucid.design': {
            'Meta': {'ordering': "('template',)", 'object_name': 'Design'},
            'colorscheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.ColorScheme']", 'null': 'True', 'blank': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'design_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'headfiles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['pylucid.EditableHtmlHeadFile']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'design_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'pylucid.editablehtmlheadfile': {
            'Meta': {'ordering': "('filepath',)", 'object_name': 'EditableHtmlHeadFile'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'editablehtmlheadfile_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filepath': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'html_attributes': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'editablehtmlheadfile_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'render': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'})
        },
        'pylucid.logentry': {
            'Meta': {'ordering': "('-createtime',)", 'object_name': 'LogEntry'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'logentry_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'data': ('dbpreferences.fields.DictField', [], {'null': 'True', 'blank': 'True'}),
            'http_accept_encoding': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_accept_language': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_referer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'logentry_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'long_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'query_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'remote_addr': ('django.db.models.fields.IPAddressField', [], {'db_index': 'True', 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'remote_user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'request_method': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'used_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']", 'null': 'True', 'blank': 'True'})
        },
        'pylucid.pagecontent': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'object_name': 'PageContent'},
            'content': ('pylucid_project.apps.pylucid.fields.MarkupContentModelField', [], {'blank': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagecontent_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagecontent_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markup': ('pylucid_project.apps.pylucid.fields.MarkupModelField', [], {}),
            'pagemeta': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pylucid.PageMeta']", 'unique': 'True'})
        },
        'pylucid.pagemeta': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'unique_together': "(('pagetree', 'language'),)", 'object_name': 'PageMeta'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagemeta_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']"}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagemeta_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pagetree': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.PageTree']"}),
            'permitViewGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagemeta_permitViewGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'robots': ('django.db.models.fields.CharField', [], {'default': "'index,follow'", 'max_length': '255', 'blank': 'True'}),
            'tags': ('django_tools.tagging_addon.fields.jQueryTagModelField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'pylucid.pagetree': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'unique_together': "(('site', 'slug', 'parent'),)", 'object_name': 'PageTree'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Design']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'page_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.PageTree']", 'null': 'True', 'blank': 'True'}),
            'permitEditGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_permitEditGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'permitViewGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_permitViewGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'showlinks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'pylucid.pluginpage': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'object_name': 'PluginPage'},
            'app_label': ('pylucid_project.apps.pylucid.fields.RootAppChoiceField', [], {'max_length': '256'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pluginpage_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pluginpage_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'pagetree': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pylucid.PageTree']", 'unique': 'True'}),
            'urls_filename': ('django.db.models.fields.CharField', [], {'default': "'urls.py'", 'max_length': '256'})
        },
        'pylucid.userprofile': {
            'Meta': {'ordering': "('user',)", 'object_name': 'UserProfile'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'userprofile_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'userprofile_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sha_login_checksum': ('django.db.models.fields.CharField', [], {'max_length': '192'}),
            'sha_login_salt': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userprofile_user'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pylucid']
