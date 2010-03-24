# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.system.pylucid_plugin import PyLucidDBPreferencesBaseForm

class PreferencesForm(PyLucidDBPreferencesBaseForm):
    template_name = forms.CharField(
        initial="rss/default.html",
        help_text=_("The default template filename.")
    )
    socket_timeout = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=60,
        help_text=_("Default socket timeout in seconds for getting the RSS feed.")
    )
    cache_timeout = forms.IntegerField(
        initial=15,
        min_value=1,
        max_value=1 * 60 * 60 * 24 * 7,
        help_text=_("Default number of seconds to cache a feed.")
    )

    class Meta:
        app_label = 'rss'
