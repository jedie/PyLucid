# coding: utf-8


from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm


class AuthPreferencesForm(DBPreferencesBaseForm):
    ban_limit = forms.IntegerField(
        help_text=_("Numbers login log messages after IP would be banned."),
        initial=6, min_value=1, max_value=20
    )
    min_pause = forms.IntegerField(
        help_text=_("Minimum pause in seconds between two login log messages from the same user. (Used 'REMOTE_ADDR')"),
        initial=5, min_value=1, max_value=600
    )

    use_honypot = forms.BooleanField(
        help_text=_("Enable login honypot? (A PluginPage must be created!)"),
        initial=False, required=False
    )

    loop_count = forms.IntegerField(
        help_text=_(
            "Number of loops in the JS-SHA1-Process for repeatedly apply"
            " the client-nonce for hash based key stretching."
            " (Note: Higher count increase the security, but causes more CPU load on client and server.)"
        ),
        initial=15, min_value=1, max_value=600
    )

    https_urls = forms.BooleanField(
        help_text=_("Use https (secure http) for login forms?"),
        initial=False, required=False
    )

    class Meta:
        app_label = 'auth'
