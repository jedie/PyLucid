# coding: utf-8

import sys

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project import VERSION_STRING
from pylucid_project.apps.pylucid.system.pylucid_plugin import PyLucidDBPreferencesBaseForm


class PreferencesForm(PyLucidDBPreferencesBaseForm):
    remote_template = forms.CharField(
        initial="include/remote_default.html",
        help_text=_("The default template filename for include remote.")
    )
    socket_timeout = forms.IntegerField(
        initial=3,
        min_value=1,
        max_value=60,
        help_text=_("Default socket timeout in seconds for getting remote data.")
    )
    cache_timeout = forms.IntegerField(
        initial=15,
        min_value=1,
        max_value=1 * 60 * 60 * 24 * 7,
        help_text=_("Default number of seconds to cache remote data.")
    )

    user_agent = forms.CharField(
        initial="Mozilla/5.0 (compatible; Python/%s; PyLucid/%s)" % (
            sys.version[:3], VERSION_STRING
        ),
        help_text=_("Use User-Agent when requesting the include remote data.")
    )

    class Meta:
        app_label = 'include'
