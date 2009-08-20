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

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid.shortcuts import failsafe_message
from pylucid.models.base_models import UpdateInfoBaseModel, BaseModel, BaseModelManager
from pylucid_project.pylucid_plugins import update_journal

# other PyLucid models
from language import Language
from pagemeta import PageMeta

TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class RootAppChoiceField(models.CharField):
    def get_choices_default(self):
        PluginPage.objects.get_app_choices()

class PluginPageManager(BaseModelManager):
    _APP_CHOICES = None
    def get_app_choices(self):
        if self._APP_CHOICES == None:
            root_apps = installed_apps_utils.get_filtered_apps(resolve_url="/")
            self._APP_CHOICES = [("", "---------")] + [(app, app) for app in root_apps]
        return self._APP_CHOICES

    def reverse(self, plugin_name, viewname, args=(), kwargs={}):
        """
        reverse a plugin url.
        Please note: this will always use the first PluginPage entry as url prefix!
        """
        # get the app label from
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        app_label = plugin_instance.pkg_string

        # Get the first PluginPage entry for this plugin
        queryset = PluginPage.objects.all()
        queryset = queryset.filter(pagemeta__page__site=Site.objects.get_current())
        queryset = queryset.filter(app_label=app_label)
        try:
            plugin_page = queryset[0]
        except (IndexError, KeyError):
            msg = "Can't get a PluginPage for plugin %r, please create one." % plugin_name
            if settings.DEBUG:
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

    pagemeta = models.ManyToManyField("PageMeta")

    app_label = RootAppChoiceField(max_length=256,
        help_text=(
            "The plugin app label witch is in settings.INSTALLED_APPS"
            " (Only apps witch can handle a root url.)"
        )
    )
    urls_filename = models.CharField(max_length=256, default="urls.py",
        help_text="Filename of the urls.py"
    )

    def get_pagemeta(self):
        lang_entry = Language.objects.get_current_lang_entry()
        try:
            return self.pagemeta.get(lang=lang_entry)
        except PageMeta.DoesNotExist:
            default_lang_entry = Language.objects.get_default_lang_entry()
            return self.pagemeta.get(lang=default_lang_entry)

    def get_site(self):
        pagemeta = self.get_pagemeta()
        return pagemeta.page.site

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        pagemeta = self.get_pagemeta()
        return pagemeta.get_absolute_url()

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
#        if not self.page.page_type == self.page.PLUGIN_TYPE:
#            # FIXME: Better error with django model validation?
#            raise AssertionError("Plugin can only exist on a plugin type tree entry!")
        return super(PluginPage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PluginPage '%s' (pagemeta: %r)" % (self.app_label, self.pagemeta.all())

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PluginPage"
        ordering = ("-lastupdatetime",)
#        ordering = ("page", "lang")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PluginPage)
