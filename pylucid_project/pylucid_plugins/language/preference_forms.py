# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm


class LanguagePrefForm(DBPreferencesBaseForm):
    add_reset_link = forms.BooleanField(
        initial = False, required = False,
        help_text = _('If checked add a reset link to the language list.'),
    )

    class Meta:
        app_label = 'language'