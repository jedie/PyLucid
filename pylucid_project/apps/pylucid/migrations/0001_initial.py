# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ColorScheme'
        db.create_table('pylucid_colorscheme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='colorscheme_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='colorscheme_lastupdateby', null=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pylucid', ['ColorScheme'])

        # Adding model 'Color'
        db.create_table('pylucid_color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='color_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='color_lastupdateby', null=True, to=orm['auth.User'])),
            ('colorscheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.ColorScheme'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('pylucid_project.apps.pylucid.fields.ColorValueField')(max_length=6)),
        ))
        db.send_create_signal('pylucid', ['Color'])

        # Adding unique constraint on 'Color', fields ['colorscheme', 'name']
        db.create_unique('pylucid_color', ['colorscheme_id', 'name'])

        # Adding model 'Design'
        db.create_table('pylucid_design', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='design_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='design_lastupdateby', null=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('colorscheme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.ColorScheme'], null=True, blank=True)),
        ))
        db.send_create_signal('pylucid', ['Design'])

        # Adding M2M table for field sites on 'Design'
        db.create_table('pylucid_design_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('design', models.ForeignKey(orm['pylucid.design'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('pylucid_design_sites', ['design_id', 'site_id'])

        # Adding M2M table for field headfiles on 'Design'
        db.create_table('pylucid_design_headfiles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('design', models.ForeignKey(orm['pylucid.design'], null=False)),
            ('editablehtmlheadfile', models.ForeignKey(orm['pylucid.editablehtmlheadfile'], null=False))
        ))
        db.create_unique('pylucid_design_headfiles', ['design_id', 'editablehtmlheadfile_id'])

        # Adding model 'EditableHtmlHeadFile'
        db.create_table('pylucid_editablehtmlheadfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='editablehtmlheadfile_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='editablehtmlheadfile_lastupdateby', null=True, to=orm['auth.User'])),
            ('filepath', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('html_attributes', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('render', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('pylucid', ['EditableHtmlHeadFile'])

        # Adding model 'LogEntry'
        db.create_table('pylucid_logentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='logentry_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='logentry_lastupdateby', null=True, to=orm['auth.User'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('long_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('data', self.gf('dbpreferences.fields.DictField')(null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('used_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.Language'], null=True, blank=True)),
            ('remote_addr', self.gf('django.db.models.fields.IPAddressField')(db_index=True, max_length=15, null=True, blank=True)),
            ('remote_user', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('request_method', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('query_string', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('http_referer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('http_user_agent', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('http_accept_encoding', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('http_accept_language', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('pylucid', ['LogEntry'])

        # Adding model 'BanEntry'
        db.create_table('pylucid_banentry', (
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pylucid', ['BanEntry'])

        # Adding model 'Language'
        db.create_table('pylucid_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='language_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='language_lastupdateby', null=True, to=orm['auth.User'])),
            ('code', self.gf('django_tools.fields.language_code.LanguageCodeModelField')(unique=True, max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('permitViewGroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='language_permitViewGroup', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('pylucid', ['Language'])

        # Adding M2M table for field sites on 'Language'
        db.create_table('pylucid_language_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('language', models.ForeignKey(orm['pylucid.language'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('pylucid_language_sites', ['language_id', 'site_id'])

        # Adding model 'PageContent'
        db.create_table('pylucid_pagecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagecontent_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagecontent_lastupdateby', null=True, to=orm['auth.User'])),
            ('pagemeta', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pylucid.PageMeta'], unique=True)),
            ('content', self.gf('pylucid_project.apps.pylucid.fields.MarkupContentModelField')(blank=True)),
            ('markup', self.gf('pylucid_project.apps.pylucid.fields.MarkupModelField')(db_column='markup_id')),
        ))
        db.send_create_signal('pylucid', ['PageContent'])

        # Adding model 'PageMeta'
        db.create_table('pylucid_pagemeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagemeta_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagemeta_lastupdateby', null=True, to=orm['auth.User'])),
            ('pagetree', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.PageTree'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.Language'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('tags', self.gf('django_tools.tagging_addon.fields.jQueryTagModelField')()),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('robots', self.gf('django.db.models.fields.CharField')(default='index,follow', max_length=255, blank=True)),
            ('permitViewGroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagemeta_permitViewGroup', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('pylucid', ['PageMeta'])

        # Adding unique constraint on 'PageMeta', fields ['pagetree', 'language']
        db.create_unique('pylucid_pagemeta', ['pagetree_id', 'language_id'])

        # Adding model 'PageTree'
        db.create_table('pylucid_pagetree', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagetree_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagetree_lastupdateby', null=True, to=orm['auth.User'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.PageTree'], null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('page_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('design', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pylucid.Design'])),
            ('showlinks', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('permitViewGroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagetree_permitViewGroup', null=True, to=orm['auth.Group'])),
            ('permitEditGroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pagetree_permitEditGroup', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('pylucid', ['PageTree'])

        # Adding unique constraint on 'PageTree', fields ['site', 'slug', 'parent']
        db.create_unique('pylucid_pagetree', ['site_id', 'slug', 'parent_id'])

        # Adding model 'PluginPage'
        db.create_table('pylucid_pluginpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pluginpage_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pluginpage_lastupdateby', null=True, to=orm['auth.User'])),
            ('pagetree', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pylucid.PageTree'], unique=True)),
            ('app_label', self.gf('pylucid_project.apps.pylucid.fields.RootAppChoiceField')(max_length=256)),
            ('urls_filename', self.gf('django.db.models.fields.CharField')(default='urls.py', max_length=256)),
        ))
        db.send_create_signal('pylucid', ['PluginPage'])

        # Adding model 'UserProfile'
        db.create_table('pylucid_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastupdatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('createby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='userprofile_createby', null=True, to=orm['auth.User'])),
            ('lastupdateby', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='userprofile_lastupdateby', null=True, to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='userprofile_user', unique=True, to=orm['auth.User'])),
            ('sha_login_checksum', self.gf('django.db.models.fields.CharField')(max_length=192)),
            ('sha_login_salt', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('pylucid', ['UserProfile'])

        # Adding M2M table for field sites on 'UserProfile'
        db.create_table('pylucid_userprofile_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['pylucid.userprofile'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('pylucid_userprofile_sites', ['userprofile_id', 'site_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PageTree', fields ['site', 'slug', 'parent']
        db.delete_unique('pylucid_pagetree', ['site_id', 'slug', 'parent_id'])

        # Removing unique constraint on 'PageMeta', fields ['pagetree', 'language']
        db.delete_unique('pylucid_pagemeta', ['pagetree_id', 'language_id'])

        # Removing unique constraint on 'Color', fields ['colorscheme', 'name']
        db.delete_unique('pylucid_color', ['colorscheme_id', 'name'])

        # Deleting model 'ColorScheme'
        db.delete_table('pylucid_colorscheme')

        # Deleting model 'Color'
        db.delete_table('pylucid_color')

        # Deleting model 'Design'
        db.delete_table('pylucid_design')

        # Removing M2M table for field sites on 'Design'
        db.delete_table('pylucid_design_sites')

        # Removing M2M table for field headfiles on 'Design'
        db.delete_table('pylucid_design_headfiles')

        # Deleting model 'EditableHtmlHeadFile'
        db.delete_table('pylucid_editablehtmlheadfile')

        # Deleting model 'LogEntry'
        db.delete_table('pylucid_logentry')

        # Deleting model 'BanEntry'
        db.delete_table('pylucid_banentry')

        # Deleting model 'Language'
        db.delete_table('pylucid_language')

        # Removing M2M table for field sites on 'Language'
        db.delete_table('pylucid_language_sites')

        # Deleting model 'PageContent'
        db.delete_table('pylucid_pagecontent')

        # Deleting model 'PageMeta'
        db.delete_table('pylucid_pagemeta')

        # Deleting model 'PageTree'
        db.delete_table('pylucid_pagetree')

        # Deleting model 'PluginPage'
        db.delete_table('pylucid_pluginpage')

        # Deleting model 'UserProfile'
        db.delete_table('pylucid_userprofile')

        # Removing M2M table for field sites on 'UserProfile'
        db.delete_table('pylucid_userprofile_sites')


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
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'primary_key': 'True'})
        },
        'pylucid.color': {
            'Meta': {'ordering': "('colorscheme', 'name')", 'unique_together': "(('colorscheme', 'name'),)", 'object_name': 'Color'},
            'colorscheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.ColorScheme']"}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'color_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'color_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'value': ('pylucid_project.apps.pylucid.fields.ColorValueField', [], {'max_length': '6'})
        },
        'pylucid.colorscheme': {
            'Meta': {'object_name': 'ColorScheme'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'colorscheme_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'colorscheme_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pylucid.design': {
            'Meta': {'ordering': "('template',)", 'object_name': 'Design'},
            'colorscheme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.ColorScheme']", 'null': 'True', 'blank': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'design_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'headfiles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['pylucid.EditableHtmlHeadFile']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'design_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'pylucid.editablehtmlheadfile': {
            'Meta': {'ordering': "('filepath',)", 'object_name': 'EditableHtmlHeadFile'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'editablehtmlheadfile_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filepath': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'html_attributes': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'editablehtmlheadfile_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'render': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        'pylucid.logentry': {
            'Meta': {'ordering': "('-createtime',)", 'object_name': 'LogEntry'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'logentry_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('dbpreferences.fields.DictField', [], {'null': 'True', 'blank': 'True'}),
            'http_accept_encoding': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_accept_language': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_referer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'logentry_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagecontent_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'markup': ('pylucid_project.apps.pylucid.fields.MarkupModelField', [], {'db_column': "'markup_id'"}),
            'pagemeta': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pylucid.PageMeta']", 'unique': 'True'})
        },
        'pylucid.pagemeta': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'unique_together': "(('pagetree', 'language'),)", 'object_name': 'PageMeta'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagemeta_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Language']"}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagemeta_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.Design']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'page_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pylucid.PageTree']", 'null': 'True', 'blank': 'True'}),
            'permitEditGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_permitEditGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'permitViewGroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pagetree_permitViewGroup'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'showlinks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'pylucid.pluginpage': {
            'Meta': {'ordering': "('-lastupdatetime',)", 'object_name': 'PluginPage'},
            'app_label': ('pylucid_project.apps.pylucid.fields.RootAppChoiceField', [], {'max_length': '256'}),
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pluginpage_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pluginpage_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pagetree': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pylucid.PageTree']", 'unique': 'True'}),
            'urls_filename': ('django.db.models.fields.CharField', [], {'default': "'urls.py'", 'max_length': '256'})
        },
        'pylucid.userprofile': {
            'Meta': {'ordering': "('user',)", 'object_name': 'UserProfile'},
            'createby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'userprofile_createby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdateby': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'userprofile_lastupdateby'", 'null': 'True', 'to': "orm['auth.User']"}),
            'lastupdatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sha_login_checksum': ('django.db.models.fields.CharField', [], {'max_length': '192'}),
            'sha_login_salt': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
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
