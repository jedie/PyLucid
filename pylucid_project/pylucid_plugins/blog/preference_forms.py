# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.site_utils import SitePreselectPreference

from dbpreferences.forms import DBPreferencesBaseForm


class BlogPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    ALL_LANGUAGES = "a"
    PREFERED_LANGUAGES = "p"
    CURRENT_LANGUAGE = "c"
    LANGUAGE_CHOICES = (
        (ALL_LANGUAGES, _("Don't filter by languages. Allways display all blog entries.")),
        (PREFERED_LANGUAGES, _("Filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)")),
        (CURRENT_LANGUAGE, _("Display only blog entries in current language (select on the page)")),
    )
    language_filter = forms.ChoiceField(initial=ALL_LANGUAGES, choices=LANGUAGE_CHOICES,
        help_text=_("How to filter blog entries by language?")
    )

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

    max_tag_count = forms.IntegerField(
        initial=5, min_value=1,
        help_text=_("The maximal numbers of tags to filter articles."),
    )
    class Meta:
        app_label = 'blog'


def get_preferences():
    pref_form = BlogPrefForm()
    preferences = pref_form.get_preferences()
    return preferences
