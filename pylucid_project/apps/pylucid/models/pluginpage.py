# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.conf import settings
from django.core import urlresolvers
from django.contrib.sites.models import Site

# http://code.google.com/p/django-tools/
from django_tools.utils import installed_apps_utils
from django_tools import model_utils

from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.apps.pylucid.models.base_models import UpdateInfoBaseModel, BaseModel, BaseModelManager


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class RootAppChoiceField(models.CharField):
    def get_choices_default(self):
        PluginPage.objects.get_app_choices()

class PluginPageManager(BaseModelManager):
    """
    TODO: In next release witch has a update routine: we should switch:
        from plugin_instance.installed_apps_string to plugin_instance.pkg_string
    """
    _APP_CHOICES = None
    def get_app_choices(self):
        """
        Generate a choice list with all views witch can handle a empty root url.
        But PyLucid can only handle own plugins, see:
            http://trac.pylucid.net/ticket/333
        """
        if self._APP_CHOICES == None:
            root_apps = installed_apps_utils.get_filtered_apps(resolve_url="/")

            self._APP_CHOICES = [("", "---------")]
            for app in root_apps:
                plugin_name = app.split(".")[-1]
                if not plugin_name in PYLUCID_PLUGINS:
                    continue
                plugin_instance = PYLUCID_PLUGINS[plugin_name]

                self._APP_CHOICES.append(
                    (plugin_instance.installed_apps_string, plugin_instance.pkg_string)
                )

#            apps = [app for app in root_apps if not "pylucid_project.apps" in app]
#            self._APP_CHOICES = [("", "---------")] + [(app, app) for app in sorted(apps)]
        return self._APP_CHOICES

    def reverse(self, plugin_name, viewname, args=(), kwargs={}):
        """
        reverse a plugin url.
        Please note: this will always use the first PluginPage entry as url prefix!
        """
        # get the app label from
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        app_label = plugin_instance.installed_apps_string

        # Get the first PluginPage entry for this plugin
        queryset = PluginPage.objects.all()
        queryset = queryset.filter(pagetree__site=Site.objects.get_current())
        queryset = queryset.filter(app_label=app_label)
        try:
            plugin_page = queryset[0]
        except (IndexError, KeyError):
            msg = "Can't get a PluginPage for plugin %r, please create one." % plugin_name
            if settings.DEBUG:
                msg += " (app_label: %r)" % app_label
                failsafe_message(msg)
            raise urlresolvers.NoReverseMatch(msg)

        url_prefix = plugin_page.get_absolute_url()
        plugin_url_resolver = plugin_instance.get_plugin_url_resolver(url_prefix, plugin_page.urls_filename)
        return plugin_url_resolver.reverse(viewname, *args, **kwargs)


class PluginPage(BaseModel, UpdateInfoBaseModel):
    """
    A plugin page

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = PluginPageManager()

    pagetree = models.OneToOneField("pylucid.PageTree")

    app_label = RootAppChoiceField(max_length=256,
        help_text=(
            "The plugin app label witch is in settings.INSTALLED_APPS"
            " (Only apps witch can handle a root url.)"
        )
    )
    urls_filename = models.CharField(max_length=256, default="urls.py",
        help_text="Filename of the urls.py"
    )

    def get_site(self):
        return self.pagetree.site

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        from pylucid_project.apps.pylucid.models import Language # import here against import loops

        pagetree_url = self.pagetree.get_absolute_url()
        lang_entry = Language.objects.get_current()
        url = "/" + lang_entry.code + pagetree_url
        return url

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        pagemeta = self.get_pagemeta()
        return pagemeta.get_title()

    def get_plugin_name(self):
        return self.app_label.split(".")[-1]

    def get_plugin(self):
        """ returns pylucid_project.system.pylucid_plugins instance """
        plugin_name = self.get_plugin_name()
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        return plugin_instance

    def save(self, *args, **kwargs):
        if not self.pagetree.page_type == self.pagetree.PLUGIN_TYPE:
            # FIXME: Better error with django model validation?
            raise AssertionError("Plugin can only exist on a plugin type tree entry!")
        return super(PluginPage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PluginPage '%s' (pagetree: %r)" % (self.app_label, self.pagetree)

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PluginPage"
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PluginPage)
