# -*- coding: utf-8 -*-
"""
    PyLucid preferences API
    ~~~~~~~~~~~~~~~~~~~~~~~

    OBSOLETE

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pformat

from django import forms

from PyLucid.models import Preference, Plugin
from PyLucid.system.plugin_import import get_plugin_module
from PyLucid.tools.data_eval import data_eval, DataEvalError

preference_cache = {}


def get_init_dict(form):
    """
    Returns a dict with all initial values from a newforms class.
    """
    init_dict = {}
    for field_name, field in form.base_fields.iteritems():
        initial = field.initial
        if initial == None:
            msg = (
                "The preferences model attribute '%s' has no initial value!"
            ) % field_name
            raise NoInitialError(msg)

        init_dict[field_name] = initial
    return init_dict


def setup_help_text(form):
    """
    Append on every help_text the default information (The initial value)
    """
    for field_name, field in form.base_fields.iteritems():
        if "(default: '" in field.help_text:
            # The default information was inserted in the past
            return
        field.help_text = "%s (default: '%s')" % (
            field.help_text, field.initial
        )


class Preferences(object):
    """
    The API class to the PyLucid.models.Preference model.
    """
    def __init__(self):
        self.plugin = None    # PyLucid.models.plugin
        self.model = None     # PyLucid.models.Preference instance
        self.data_dict = None # dictionary object of the preferences data
        self.form = None      # PreferencesForm from the plugin modul

    def set_plugin(self, plugin_instance):
        """
        used in:
         - plugin_manager._run()
         - plugin_manager._insert_preferences()
        """
        self.plugin = plugin_instance

    def init_via_id(self, id):
        """
        Load PyLucid.models.Preference via the id of the Preference entry.
        """
        if self.model == None:
            self.init_via_get(id = id)

    def load_from_db(self):
        """
        load the dict_data from db
        """
        if self.plugin == None:
            raise InitError("plugin not loaded.")

        if self.model == None:
            self.init_via_get(plugin = self.plugin)

    #__________________________________________________________________________
    def init_via_get(self, **kwargs):
        """
        Get the model from db and set data_dict + plugin
        """
        try:
            self.model = Preference.objects.get(**kwargs)
        except Preference.DoesNotExist, e:
            raise PreferenceDoesntExist(e)

        self.data_dict = data_eval(self.model.repr_string)
        self.plugin = self.model.plugin

    #__________________________________________________________________________

    def create_initial(self, pref_form):
        """
        Insert a new Preference entry in the database.

        perf_fomr -- django forms.Form class

        Use the newforms initial values as the dict_data.
        """
        if self.plugin == None:
            raise InitError("plugin not loaded.")

        init_dict = get_init_dict(pref_form)
        preference_cache[self.plugin.plugin_name] = init_dict

        repr_string = pformat(init_dict)

        self.model = Preference(plugin = self.plugin, repr_string = repr_string)
        self.model.save()

    #__________________________________________________________________________

    def load_form(self, request):
        """
        load PreferencesForm class from the plugin modul.
        """
        if self.plugin == None:
            raise InitError("plugin not loaded.")

        plugin_module = get_plugin_module(
            request, self.plugin.package_name, self.plugin.plugin_name
        )

        form = getattr(plugin_module, "PreferencesForm")
        setup_help_text(form)
        self.form = form


    #__________________________________________________________________________

    def update_and_save(self, new_data_dict):
        """
        update the data_dict in the model and save it.
        """
        if self.model == None:
            raise InitError("model not loaded.")

        self.data_dict.update(new_data_dict)

        preference_cache[self.plugin.plugin_name] = self.data_dict

        self.model.repr_string = pformat(self.data_dict)
        self.model.save()



def get_all_prefs():
    """
    returns a list of all existing preferences entries in the database
    """
    return Preference.objects.all()


def get_pref_dict(plugin_name):
    """
    returns the data_dict for the given plugin_name. Used the cache.
    If a plugin use preferences in a newforms, it must have access to the
    preferences at module level.
    FIXME: If the admin change the preferences, the values in a plugin module
    level would only updated, if the server instance restarted.
    """
    if plugin_name in preference_cache:
        return preference_cache[plugin_name]

    plugin = Plugin.objects.get(plugin_name=plugin_name)

    p = Preferences()
    p.set_plugin(plugin)
    p.load_from_db()
    return p.data_dict


#______________________________________________________________________________
# Exceptions

class InitError(Exception):
    """
    The init state of Preferences class is wrong
    """
    pass

class NoInitialError(Exception):
    """
    All preferences newform attributes must habe a initial value.
    """
    pass

class PreferenceDoesntExist(Preference.DoesNotExist):
    pass