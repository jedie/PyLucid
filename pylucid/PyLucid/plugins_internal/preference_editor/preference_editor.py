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

from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Plugin, Preference

class CommentForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ('comment',)


class preference_editor(PyLucidBasePlugin):

    def _vebose_plugin_name(self, pref):
        return pref.plugin.plugin_name.replace("_", " ")

    def select(self):
        """
        Display the sub menu
        """
        plugins = Plugin.objects.exclude(default_pref__isnull=True)

        context = {
            "plugins": plugins,
            "edit_link": self.URLs.methodLink("edit"),
            "add_link": self.URLs.methodLink("add"),
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

        pref = Preference.objects.get(id = pref_id)
        plugin = pref.plugin
        unbound_form = plugin.get_pref_form(self.page_msg, self.request.debug)

        if self.request.method == 'POST':
            form = unbound_form(self.request.POST)
            if form.is_valid():
                new_data_dict = form.cleaned_data

                pref.set_data(new_data_dict, self.request.user)
                pref.save()
                self.page_msg("New preferences saved.")
                return self.select() # Display the menu
        else:
            data_dict = pref.get_data()
            form = unbound_form(data_dict)

        context = {
            "plugin_name": unicode(plugin),
            "form": form,
            "url_abort": self.URLs.methodLink("select"),
        }

        # Insert DocString from preferences form, if exist
        raw_doc = unbound_form.__doc__
        if raw_doc:
            doc = raw_doc.strip().splitlines()
            context["doc"] = "\n".join([line.strip() for line in doc if line])

        self._render_template("edit_form", context)#, debug=True)

    def add(self, url_args):
        try:
            url_args = url_args.strip("/")
            plugin_id = int(url_args)
        except Exception, e:
            self.page_msg.red("url error:", e)
            return

        plugin = Plugin.objects.get(id = plugin_id)

        if self.request.method == 'POST':
            form = CommentForm(self.request.POST)
            if form.is_valid():
                default_pref_data = plugin.default_pref.get_data()
                new_pref = plugin.add_preference(
                    comment = form.cleaned_data["comment"],
                    data = default_pref_data,
                    user = self.request.user,
                )
                self.page_msg("New preferences added.")
                return self.select() # Display the menu
        else:
            form = CommentForm()#instance=new_pref)

        context = {
            "plugin_name": unicode(plugin),
            "form": form,
            "url_abort": self.URLs.methodLink("select"),
        }
        self._render_template("edit_form", context)#, debug=True)





