# -*- coding: utf-8 -*-

"""
    Preferences
    ~~~~~~~~~~~

    A low level editor for the preferences.
    Using data_eval and pprint. Supports only Constants, Dicts, Lists, Tuples.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev: $"

from pprint import pformat

from django import newforms as forms
from django.newforms.util import ValidationError
from django.utils.translation import ugettext as _

from PyLucid.db.preferences import get_all_prefs, Preferences
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.data_eval import data_eval, DataEvalError



class preferences(PyLucidBasePlugin):

    def _vebose_plugin_name(self, pref):
        return pref.plugin.plugin_name.replace("_", " ")

    def select(self):
        """
        Display the sub menu
        """
        self.context["PAGE"].title = _("preferences editor")

        items = []
        for pref in get_all_prefs():
            edit_link = self.URLs.methodLink("edit", args=pref.id)

            items.append({
                "plugin_name": self._vebose_plugin_name(pref),
                "plugin_description": pref.plugin.description,
                "edit_link": edit_link,
            })

        context = {
            "preferences": items,
            "admin_link": self.URLs.adminLink("PyLucid/preference"),
        }
        self._render_template("select", context)#, debug=True)

    def edit(self, url_args):
        try:
            url_args = url_args.strip("/")
            pref_id = int(url_args)
        except Exception, e:
            self.page_msg.red("url error:", e)
            return

        p = Preferences()
        p.init_via_id(pref_id)
        data_dict = p.data_dict

        p.load_form(self.request)
        unbound_form = p.form

        if self.request.method == 'POST':
            form = unbound_form(self.request.POST)
            if form.is_valid():
                new_data_dict = form.cleaned_data
                p.update_and_save(new_data_dict)
                self.page_msg("New preferences saved.")
                return self.select() # Display the menu
        else:
            form = unbound_form(data_dict)

        context = {
            "plugin_name": self._vebose_plugin_name(p),
            "form": form,
            "url_abort": self.URLs.methodLink("select"),
        }
        self._render_template("edit_form", context)#, debug=True)







