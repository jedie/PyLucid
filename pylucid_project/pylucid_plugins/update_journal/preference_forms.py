# coding: utf-8

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
    class Meta:
        app_label = 'update_journal'
