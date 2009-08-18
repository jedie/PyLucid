# coding: utf-8

import warnings

from django import forms
from django.utils.translation import ugettext_lazy as _

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid.models import PageTree, Design, Language

if Language.objects.count() == 0:
    # FIXME: Insert first language
    Language(code="en", description="english").save()
    warnings.warn("First language 'en' created.")


class SystemPreferencesForm(DBPreferencesBaseForm):
    """ test preferences form """
    pylucid_admin_design = forms.ChoiceField(
        choices=Design.objects.values_list('id', 'name'),
        required=False, initial=None,
        help_text=_("ID of the PyLucid Admin Design.")
    )
    lang_code = forms.ChoiceField(
        choices=Language.objects.values_list('code', 'description'),
        initial=Language.objects.all()[0].code,
        help_text=_("Default language")
    )
    ban_release_time = forms.IntegerField(
        help_text=_("How long should a IP address banned in minutes. (Changes need app restart)"),
        initial=15, min_value=1, max_value=60 * 24 * 7
    )

    class Meta:
        app_label = 'pylucid'
