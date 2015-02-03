# coding: utf-8


"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete

# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.models import UpdateInfoBaseModel
from django_tools.utils import installed_apps_utils
from django_tools.utils.messages import failsafe_message

from pylucid_project.apps.pylucid.fields import RootAppChoiceField
from pylucid_project.apps.pylucid.signals_handlers import update_plugin_urls
from pylucid_project.base_models.base_models import BaseModelManager, BaseModel
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


_URL_RESOLVER_CACHE = LocalSyncCache(id="PluginPage_url_resolver")


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
            debug = settings.DEBUG and settings.RUN_WITH_DEV_SERVER

            root_apps = installed_apps_utils.get_filtered_apps(
                resolve_url="/", no_args=False, debug=debug, skip_fail=True
            )

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

    def queryset_by_app_label(self, app_label, site=None):
        """
        queryset to get PluginPages on current a site by app_label
        """
        if site is None:
            site = Site.objects.get_current()

        queryset = PluginPage.objects.all()
        queryset = queryset.filter(pagetree__site=site)
        queryset = queryset.filter(app_label=app_label)
        return queryset

    def queryset_by_plugin_name(self, plugin_name, site=None):
        """
        queryset to get PluginPages on current a site by app_label
        
        usage, e.g:
        queryset = PluginPage.objects.queryset_by_plugin_name("blog")
        """
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        app_label = plugin_instance.installed_apps_string
        queryset = self.queryset_by_app_label(app_label)
        return queryset

    def get_by_plugin_name(self, plugin_name):
        """
        return PluginPage instance by plugin_name
        """
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        app_label = plugin_instance.installed_apps_string

        queryset = self.queryset_by_app_label(app_label)
        try:
            # Get the first PluginPage entry for this plugin
            plugin_page = queryset[0]
        except (IndexError, KeyError):
            msg = "Can't get a PluginPage for plugin %r, please create one." % plugin_name
            if settings.DEBUG:
                msg += " (app_label: %r)" % app_label
                failsafe_message(msg)
            raise urlresolvers.NoReverseMatch(msg)
        return plugin_page

    def get_url_resolver(self, plugin_name):
        """
        return a url resolver for the given plugin
        """
        try:
            plugin_url_resolver = _URL_RESOLVER_CACHE[plugin_name]
        except KeyError:
            plugin_instance = PYLUCID_PLUGINS[plugin_name]
            plugin_page = self.get_by_plugin_name(plugin_name)

            url_prefix = plugin_page.get_absolute_url()
            plugin_url_resolver = plugin_instance.get_plugin_url_resolver(url_prefix, plugin_page.urls_filename)
            _URL_RESOLVER_CACHE[plugin_name] = plugin_url_resolver
        return plugin_url_resolver

    def reverse(self, plugin_name, viewname, args=(), kwargs={}):
        """
        reverse a plugin url.
        Please note: this will always use the first PluginPage entry as url prefix!
        """
        plugin_url_resolver = self.get_url_resolver(plugin_name)
        url = plugin_url_resolver.reverse(viewname, *args, **kwargs)
        return url


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
        language_entry = Language.objects.get_current()
        url = "/" + language_entry.code + pagetree_url
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

        _URL_RESOLVER_CACHE.clear()

        # FIXME: We must only update the cache for the current SITE not for all sites.
        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

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

post_save.connect(update_plugin_urls, sender=PluginPage)
post_delete.connect(update_plugin_urls, sender=PluginPage)
