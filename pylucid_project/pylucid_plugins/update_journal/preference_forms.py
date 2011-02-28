# coding: utf-8


"""
    PyLucid update journal preferences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p
"""


from django import forms
from django.utils.translation import ugettext_lazy as _

from dbpreferences.forms import DBPreferencesBaseForm


class UpdateJournalPrefForm(DBPreferencesBaseForm):
    initial_feed_count = forms.IntegerField(
        initial=5, min_value=1,
        help_text=_("Default numbers of UpdateJournal entries in RSS/Atom feed."),
    )
    max_feed_count = forms.IntegerField(
        initial=30, min_value=1,
        help_text=_("The maximal numbers of UpdateJournal entries in RSS/Atom feed."),
    )
    current_language_only = forms.BooleanField(
        initial=True, required=False,
        help_text=_("Display only updates in current language (checked) or in every languages (unchecked).")
    )
    class Meta:
        app_label = 'update_journal'
