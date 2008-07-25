# -*- coding: utf-8 -*-
"""
    PyLucid.models.Plugin
    ~~~~~~~~~~~~~~~~~~~

    Database model for Plugin.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os, inspect
from pprint import pformat

from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.db import models, transaction, connection

from PyLucid.system.plugin_import import get_plugin_module, \
                                        get_plugin_config, get_plugin_version
from PyLucid.tools.forms_utils import get_init_dict, setup_help_text
from PyLucid.tools.data_eval import data_eval, DataEvalError
from PyLucid.system.exceptions import PluginPreferencesError

#preference_cache = {}
PLUGIN_MODEL_LABEL = "PyLucidPlugins"
PLUGIN_MODEL_APP = "PyLucid.system.PyLucidPlugins"


def get_plugin_models(package_name, plugin_name, page_msg, verbosity):
    """
    returns a list of all existing plugin models.
    If no models exist, returns None!

    Seperated function, because must be accessible from manager- and plugin
    class, too.
    """
    plugin_module = get_plugin_module(package_name, plugin_name)
    if not hasattr(plugin_module, "PLUGIN_MODELS"):
        # Plugin has no models
        return None

    if not PLUGIN_MODEL_APP in settings.INSTALLED_APPS:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            "Error '%s' not in settings.INSTALLED_APPS!" % PLUGIN_MODEL_APP
        )

    plugin_models = plugin_module.PLUGIN_MODELS

    # Check app_label for every plugin model
    for model in plugin_models:
        app_label = model._meta.app_label
        assert app_label == PLUGIN_MODEL_LABEL, (
            "Plugin model '%r' must defined in class Meta: app_label = '%s'"
        ) % (model, PLUGIN_MODEL_LABEL)

    return plugin_models





class PluginManager(models.Manager):
    """
    Manager class for Plugin objects.

    Adds caching to plugin preference queries.
    """
    def get_pref_obj(self, plugin_name, id=None):
        # Get the name of the plugin, if __file__ used
        plugin_name = os.path.splitext(os.path.basename(plugin_name))[0]
        #print "plugin name: '%s'" % plugin_name

#        if plugin_name in preference_cache:
#            return preference_cache[plugin_name]

        plugin = self.get(plugin_name = plugin_name)

        if id==None:
            # get the default entry
            pref = plugin.default_pref
            if pref==None:
                return None
        else:
            id = int(id) # FIXME: for http://trac.pylucid.net/ticket/202
            pref = Preference.objects.get(id = id)
            assert pref.plugin == plugin, (
                "Preference ID %s is wrong."
                " This entry is for the plugin '%s' and not for '%s'!"
            ) % (id, pref.plugin, plugin)

        return pref

    def get_preferences(self, plugin_name, id=None):
        """
        returns the preference data dict, use the cache
        """
        pref = self.get_pref_obj(plugin_name, id)
        data_dict = pref.get_data()
        return data_dict

    def set_preferences(self, plugin_name, key, value, user, id=None):
        """
        set a new value to one preferences entry
        """
        pref_obj = self.get_pref_obj(plugin_name, id)
        data_dict = pref_obj.get_data()
        data_dict[key] = value
        pref_obj.set_data(data_dict, user)
        pref_obj.save()
        return data_dict

    def get_plugin_models(self, package_name, plugin_name, page_msg, verbosity):
        """ returns a list of all existing plugin models or None """
        return get_plugin_models(package_name, plugin_name, page_msg, verbosity)

    def method_filter(self, queryset, method_name, page_msg, verbosity):
        """
        Returns a list of all plugins witch have the given method.
        """
        def _has_method(methods, method_name):
            for method in methods:
                if method[0] == method_name:
                    return True

        result = []
        for plugin in queryset.all():
            try:
                methods = plugin.get_all_methods()
            except Exception, err:
                if verbosity:
                    page_msg.red(
                        "Error getting plugin methods %s.%s: %s" % (
                            plugin.package_name, plugin.plugin_name, err
                        )
                    )
                    continue

            if _has_method(methods, "feed"):
                result.append(plugin)

        return result


class Plugin(models.Model):
    """
    Model for Plugin administration.
    """
    objects = PluginManager()

    plugin_name = models.CharField(max_length=90, unique=True)

    package_name = models.CharField(max_length=255)
    author = models.CharField(blank=True, max_length=150)
    url = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=255)

    multiple_pref = models.BooleanField(
        default = True,
        help_text = "Can this Plugin have multiple preferences or not?"
    )

    default_pref = models.ForeignKey(
        "Preference", related_name="plugin_default_pref",
        null=True, blank=True,
        help_text=(
            "Witch preferences used as default"
            " (If no id specified in lucidTag)"
        )
    )

    can_deinstall = models.BooleanField(
        default=True,
        help_text=(
            "If false and/or not set:"
            " This essential plugin can't be deinstalled."
        )
    )
    active = models.BooleanField(
        default=False,
        help_text="Is this plugin is enabled and useable?"
    )

    #__________________________________________________________________________
    # Special methods

    def init_pref_form(self, pref_form, page_msg, verbosity, user, id=None):
        """
        Set self.pref_data_string from the given newforms form and his initial
        values.
        Before we save the data dict into the database, we validate it with
        preferences newform class. This is needed for two cased:
         - A plugin developer has inserted a wrong initial value
         - The initial value must be cleaned. e.g. admin_menu_cfg.WeightField
        """
        if verbosity:
            page_msg("Save initial preferences.")

        init_dict = get_init_dict(pref_form)

        # Validate the init_dict
        unbound_form = self.get_pref_form(page_msg, verbosity)

        form = unbound_form(init_dict)
        if form.is_valid():
            cleaned_data_dict = form.cleaned_data
        else:
            msg = (
                "Can't save preferences for %s.%s into the database!"
                " Newforms validate error: %r"
            ) % (self.package_name, self.plugin_name, form.errors)
            raise PluginPreferencesError(msg)

        if verbosity>1:
            page_msg("Initial preferences:")
            page_msg(cleaned_data_dict)

#        preference_cache[self.plugin_name] = cleaned_data_dict

        self.set_default_preference(
            comment = "default preference entry",
            data = cleaned_data_dict,
            user = user,
        )

    def get_version_string(self):
        """
        Returned the version string from the plugin module
        """
        return get_plugin_version(self.package_name, self.plugin_name)

    def get_plugin_models(self, page_msg, verbosity):
        """ returns a list of all existing plugin models or None """
        return get_plugin_models(
            self.package_name, self.plugin_name, page_msg, verbosity
        )

    def get_pref_form(self, page_msg, verbosity):
        """
        Get the 'PreferencesForm' newform class from the plugin modul, insert
        initial information into the help text and return the form.
        """
        plugin_config = get_plugin_config(self.package_name, self.plugin_name)
        form = getattr(plugin_config, "PreferencesForm")
        if verbosity>1:
            page_msg("setup preferences form help text.")
        setup_help_text(form)
        return form

    #__________________________________________________________________________
    # PLUGIN MODULE

    def get_class(self):
        """
        returns the plugin class object
        """
        plugin_module = get_plugin_module(self.package_name, self.plugin_name)
        plugin_class = getattr(plugin_module, self.plugin_name)
        return plugin_class

    def get_all_methods(self):
        """
        returns all plugin class methods.
        tuple from inspect.getmembers()
        (Without methods starts with underscore)
        """
        plugin_class = self.get_class()
        result = []
        for method in inspect.getmembers(plugin_class, inspect.ismethod):
            if not method[0].startswith("_"):
                result.append(method)
        return result

    #__________________________________________________________________________
    # PREFERENCES

    def get_preference(self, id):
        """
        Returns the preference model entry.
        """
        pref = Preference.objects.get(id = id)
        return pref

    def get_all_preferences(self):
        """
        Returns all preference entries for this plugin except the default entry.
        """
        prefs = Preference.objects.filter(plugin = self)
        if self.default_pref:
            # execlude the default preference entry
            prefs = prefs.exclude(id = self.default_pref.id)

        return prefs

    def add_preference(self, comment, data, user):
        """
        Add a new preference data dict.
        """
        # Create a new preference entry
        p = Preference.objects.create(
            user, data,
            plugin = self,
            comment = comment,
        )
        p.save()
        return p

    def udpate_preference(self, comment, data, id, user):
        pref = Preference.objects.get(id = id)
        pref.set_data(data, user)
        pref.comment = comment
        pref.save()
        return pref

    def set_default_preference(self, comment, data, user):
        """
        Create or update the default preference entry
        """
        if self.default_pref == None:
            # First time the default preference created
            self.default_pref = Preference.objects.create(
                user, data,
                plugin = self,
                comment = comment,
            )
        else:
            # Update a existing preferences
            self.default_pref.set_data(data, user)
            self.default_pref.comment = comment

        self.default_pref.save()
        self.save()
        return self.default_pref

    #__________________________________________________________________________
    # SAVE

    def save(self):
        """
        Save a new plugin or update changed data.
        before save: check some data consistency to prevents inconsistent data.
        """
        if self.can_deinstall==False:
            # This plugin can't be deactivaded!
            # If reinit misses, the plugin is deinstalled. After a install with
            # the plugin admin, normaly the plugin would not be acivated
            # automaticly. So we activated it here:
            self.active = True

        super(Plugin, self).save() # Call the "real" save() method

    #___________________________________________________________________________
    # DELETE

    def get_delete_sql(self, plugin_models):
        """
        Returns a list of sql statements for deleting the plugin model tabels.
        For this, we used the fake django app "PyLucidPlugins" and attach
        all models to this add temporarly.
        """
        from django.core.management import sql
        from django.core.management.color import no_style
        style = no_style()

        models.loading.register_models("PyLucidPlugins", *plugin_models)

        app = models.get_app("PyLucidPlugins")

        statements = sql.sql_delete(app, style)

        # cleanup
        app_models = models.loading.cache.app_models
        del(app_models["PyLucidPlugins"])

        return statements

    def _delete_tables(self, page_msg, verbosity):
        """
        Delete all plugin model tabels.
        """
        try:
            plugin_models = self.get_plugin_models(page_msg, verbosity)
        except ImportError, err:
            # Plugin deleted in the filesystem, so we can't deinstall existing
            # models
            if verbosity>1:
                raise
            page_msg.red("Can't get plugin model list: %s" % err)

        if not plugin_models:
            if verbosity>1:
                page_msg.green("Plugin has no models, ok.")
            return

        statements = self.get_delete_sql(plugin_models)

        cursor = connection.cursor()
        for statement in statements:
            if verbosity>1:
                page_msg(statement)
            cursor.execute(statement)

        if verbosity:
            page_msg.green("%i plugin models deleted." % len(plugin_models))


    @transaction.commit_on_success
    def delete(self, page_msg, verbosity):
        page_msg(
            _("Deinstall plugin %s.%s:") % (self.package_name, self.plugin_name)
        )
        self._delete_tables(page_msg, verbosity)

        super(Plugin, self).delete()

    #___________________________________________________________________________
    # META

    class Meta:
        permissions = (
            # Permission identifier     human-readable permission name
            ("can_use",                 "Can use the plugin"),
        )

    def __unicode__(self):
        return self.plugin_name.replace(u"_",u" ")

    class Meta:
        db_table = 'PyLucid_plugin'
        app_label = 'PyLucid'


class PluginAdmin(admin.ModelAdmin):
    list_display = (
        "active", "plugin_name", "description", "can_deinstall"
    )
    list_display_links = ("plugin_name",)
    ordering = ('package_name', 'plugin_name')
    list_filter = ("author","package_name", "can_deinstall")

admin.site.register(Plugin, PluginAdmin)


#______________________________________________________________________________
# PREFERENCES



class PreferencesManager(models.Manager):
    """
    Manager class for Preference objects.

    Adds caching to plugin preference queries.
    """
    def create(self, user, data, **kwargs):
        """
        Create a new preferences entry and save the data into pref_data_string
        """
        kwargs["createby"] = user
        pref = super(PreferencesManager, self).create(**kwargs)
        pref.set_data(data, user)
        pref.save()
        return pref




class Preference(models.Model):
    """
    Plugin preferences
    """
    objects = PreferencesManager()

    id = models.AutoField(primary_key=True,
        help_text="The id of this preference entry, used for lucidTag"
    )
    plugin = models.ForeignKey(Plugin)

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False, related_name="pref_createby",
        help_text="User how create the current page.",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, related_name="pref_lastupdateby",
        help_text="User as last edit the current entry.",
        null=True, blank=True
    )

    comment = models.CharField(max_length=255,
        help_text="Small comment for this preference entry"
    )
    pref_data_string = models.TextField(
        null=False, blank=False,
        help_text="printable representation of the newform data dictionary"
    )

    #__________________________________________________________________________
    # Special set methods

    def set_data(self, data_dict, user):
        """
        set the dict via pformat
        """
#        preference_cache[self.plugin_name] = data_dict
        self.pref_data_string = pformat(data_dict)
        self.lastupdateby = user

    #__________________________________________________________________________
    # Special get methods

    def get_data(self):
        """
        evaluate the pformat string into a dict and return it.
        """
        data_dict = data_eval(self.pref_data_string)
#        preference_cache[self.plugin_name] = data_dict
        return data_dict

    #__________________________________________________________________________

    def __unicode__(self):
        return u"Preferences for %s.%s, id: %s" % (
            self.plugin.package_name, self.plugin.plugin_name, self.id
        )

    class Meta:
        db_table = 'PyLucid_preference'
        app_label = 'PyLucid'


class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "plugin", "comment",
    )
    list_display_links = ("comment",)
    ordering = ("plugin", "id")
    list_filter = ("plugin",)

admin.site.register(Preference, PreferenceAdmin)