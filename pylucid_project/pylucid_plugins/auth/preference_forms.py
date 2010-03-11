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
        initial=15, min_value=1, max_value=600
    )

    class Meta:
        app_label = 'auth'
