#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid system settings
    ~~~~~~~~~~~~~~~~~~~~~~~

    A pseudo plugin for holding the system settings via the plugin preferences.

    TODO: merge with page_admin ChoiceField -> move it into PyLucid.db.page?

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author: JensDiemer $

    :copyright: 2008 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

from django import newforms as forms
#from django.utils.translation import ugettext as _
#from django.utils.safestring import mark_safe

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page
from PyLucid.db.page import flat_tree_list

def get_parent_choices():
    """
    generate a verbose page name tree for the parent choice field.
    """
    page_list = flat_tree_list()
    choices = [(0, "---[root]---")]
    for page in page_list:
        choices.append((page["id"], page["level_name"]))
    return choices

class PreferencesForm(forms.Form):
#    index_page = forms.IntegerField(
    index_page = forms.ChoiceField(
        choices=get_parent_choices(),
        help_text="The page ID of the index page",
        initial=0
    )
    auto_shortcuts = forms.BooleanField(
        help_text="Should the shortcut of a page rebuild on every edit?",
        initial=True
    )



class system_settings(PyLucidBasePlugin):

    def lucidTag(self):
        """
        Insert a empty search form into the page.
        """
        self.page_msg("Preferences:", self.preferences)
