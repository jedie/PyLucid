# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.site_utils import SitePreselectPreference

from dbpreferences.forms import DBPreferencesBaseForm


class BlogPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    max_anonym_count = forms.IntegerField(
        initial=10, min_value=1,
        help_text=_(
            "The maximal numbers of blog entries, displayed together"
            " for anonymous users"
        ),
    )
    max_user_count = forms.IntegerField(
        initial=30, min_value=1,
        help_text=_(
            "The maximal numbers of blog entries, displayed together"
            " for logged in PyLucid users."
        ),
    )
    
    initial_feed_count = forms.IntegerField(
        initial=5, min_value=1,
        help_text=_("Default numbers of blog articles in RSS/Atom feed."),
    )
    max_feed_count = forms.IntegerField(
        initial=30, min_value=1,
        help_text=_("The maximal numbers of blog articles in RSS/Atom feed."),
    )
    class Meta:
        app_label = 'blog'
