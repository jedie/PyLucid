# -*- coding: utf-8 -*-

"""
    Preferences
    ~~~~~~~~~~~

    A low level editor for the preferences.
    Using data_eval and pprint. Supports only Constants, Dicts, Lists, Tuples.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev:1549 $
    $Author:JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

__version__= "$Rev: $"

from pprint import pformat

from django import newforms as forms
from django.newforms.util import ValidationError
from django.utils.translation import ugettext as _

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Plugin



class preference_editor(PyLucidBasePlugin):

    def _vebose_plugin_name(self, pref):
        return pref.plugin.plugin_name.replace("_", " ")

    def select(self):
        """
        Display the sub menu
        """
        plugins = Plugin.objects.exclude(pref_data_string__isnull=True)

        # Add edit link
        for plugin in plugins:
            edit_link = self.URLs.methodLink("edit", args=plugin.id)
            plugin.edit_link = edit_link

        context = {
            "plugins": plugins,
            "admin_link": self.URLs.adminLink("PyLucid/Plugin"),
        }
        self._render_template("select", context)#, debug=True)

    def edit(self, url_args):
        try:
            url_args = url_args.strip("/")
            plugin_id = int(url_args)
        except Exception, e:
            self.page_msg.red("url error:", e)
            return

        plugin = Plugin.objects.get(id = plugin_id)
        unbound_form = plugin.get_pref_form(self.page_msg, self.request.debug)

        if self.request.method == 'POST':
            form = unbound_form(self.request.POST)
            if form.is_valid():
                new_data_dict = form.cleaned_data

                plugin.set_pref_data_string(new_data_dict)
                plugin.save()
                self.page_msg("New preferences saved.")
                return self.select() # Display the menu
        else:
            data_dict = plugin.get_preferences()
            form = unbound_form(data_dict)

        context = {
            "plugin_name": unicode(plugin),
            "form": form,
            "url_abort": self.URLs.methodLink("select"),
        }
        self._render_template("edit_form", context)#, debug=True)







