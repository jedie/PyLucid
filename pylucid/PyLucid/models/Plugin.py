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

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os
from pprint import pformat

from django.db import models, transaction, connection
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from PyLucid.system.plugin_import import get_plugin_module, \
                                                                        get_plugin_config, get_plugin_version
from PyLucid.tools.newforms_utils import get_init_dict, setup_help_text
from PyLucid.tools.data_eval import data_eval, DataEvalError
from PyLucid.system.exceptions import PluginPreferencesError

preference_cache = {}

class PluginManager(models.Manager):
    """
    Manager class for Plugin objects.

    Adds caching to plugin preference queries.
    """
    def get_preferences(self, plugin_name):
        """
        returns the preference data dict, use the cache
        """
        # Get the name of the plugin, if __file__ used
        plugin_name = os.path.splitext(os.path.basename(plugin_name))[0]
        #print "plugin name: '%s'" % plugin_name

        if plugin_name in preference_cache:
            return preference_cache[plugin_name]

        plugin = self.get(plugin_name = plugin_name)
        return plugin.get_preferences()


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

    pref_data_string = models.TextField(
        null=True, blank=True,
        help_text="printable representation of the newform data dictionary"
    )
    can_deinstall = models.BooleanField(default=True,
        help_text=(
            "If false and/or not set:"
            " This essential plugin can't be deinstalled."
        )
    )
    active = models.BooleanField(default=False,
        help_text="Is this plugin is enabled and useable?"
    )

    #__________________________________________________________________________
    # Special methods

    def init_pref_form(self, pref_form, debug=False):
        """
        Set self.pref_data_string from the given newforms form and his initial
        values.
        Before we save the data dict into the database, we validate it with
        preferences newform class. This is needed for two cased:
         - A plugin developer has inserted a wrong initial value
         - The initial value must be cleaned. e.g. admin_menu_cfg.WeightField
        """
        init_dict = get_init_dict(pref_form)

        # Validate the init_dict
        unbound_form = self.get_pref_form(debug)
        form = unbound_form(init_dict)
        if form.is_valid():
            cleaned_data_dict = form.cleaned_data
        else:
            msg = (
                "Can't save preferences into the database!"
                " Newforms validate error: %r"
            ) % form.errors
            raise PluginPreferencesError(msg)

        preference_cache[self.plugin_name] = cleaned_data_dict
        self.set_pref_data_string(cleaned_data_dict)

    #__________________________________________________________________________
    # Special set methods

    def set_pref_data_string(self, data_dict):
        """
        set the dict via pformat
        """
        preference_cache[self.plugin_name] = data_dict
        self.pref_data_string = pformat(data_dict)

    #__________________________________________________________________________
    # Special get methods

    def get_preferences(self):
        """
        evaluate the pformat string into a dict and return it.
        """
        if self.pref_data_string == None:
            # There exist no preferences (e.g. plugin update not applied, yet)
            data_dict = None
        else:
            data_dict = data_eval(self.pref_data_string)
        preference_cache[self.plugin_name] = data_dict
        return data_dict

    def get_pref_form(self, debug):
        """
        Get the 'PreferencesForm' newform class from the plugin modul, insert
        initial information into the help text and return the form.
        """
        plugin_config = get_plugin_config(
            self.package_name, self.plugin_name, debug
        )
        form = getattr(plugin_config, "PreferencesForm")
        setup_help_text(form)
        return form

    def get_version_string(self, debug=False):
        """
        Returned the version string from the plugin module
        """
        return get_plugin_version(self.package_name, self.plugin_name, debug)

    #___________________________________________________________________________
    # SAVE

    def save(self):
        """
        Save a new plugin or update changed data.
        before save: check some data consistency to prevents inconsistent data.
        """
        if self.can_deinstall==False and self.active==False:
            # This plugin can't be deactivaded!
            # If reinit misses, the plugin is deinstalled. After a install with
            # the plugin admin, normaly the plugin would not be acivated
            # automaticly. So we activated it here:
            self.active = True

        super(Plugin, self).save() # Call the "real" save() method

    #___________________________________________________________________________
    # DELETE

    def get_delete_sql(self, plugin_models):
#        from django.conf import settings
        from django.core.management.color import no_style
        style = no_style()
        from django.core.management import sql

        models.loading.register_models("PyLucidPlugins", *plugin_models)

        # get all delete statements for the given App
        app = models.get_app("PyLucidPlugins")
        statements = sql.sql_delete(app, style)

        print sql.table_list()

        #cleanup
        app_models = models.loading.cache.app_models
        del(app_models["PyLucidPlugins"])
    #    settings.INSTALLED_APPS = old_inst_apps

        return statements

    def get_delete_tables(self):
        plugin_module = get_plugin_module(
            self.package_name,
            self.plugin_name,
            debug=True,
        )
        if not hasattr(plugin_module, "PLUGIN_MODELS"):
            # Plugin has no models
            return

        plugin_models = plugin_module.PLUGIN_MODELS

        statements = self.get_delete_sql(plugin_models)

        cursor = connection.cursor()
        for statement in statements:
            print repr(statement)
            cursor.execute(statement)


    @transaction.commit_on_success
    def delete(self):
        self.get_delete_tables()

        super(Plugin, self).delete()

    #___________________________________________________________________________
    # META

    class Meta:
        permissions = (
            # Permission identifier     human-readable permission name
            ("can_use",                 "Can use the plugin"),
        )

    class Admin:
        list_display = (
            "active", "plugin_name", "description", "can_deinstall"
        )
        list_display_links = ("plugin_name",)
        ordering = ('package_name', 'plugin_name')
        list_filter = ("author","package_name", "can_deinstall")

    def __unicode__(self):
        txt = u"%s - %s" % (self.package_name, self.plugin_name)
        return txt.replace(u"_",u" ")

    class Meta:
        db_table = 'PyLucid_plugin'
        app_label = 'PyLucid'
