# coding: utf-8

import warnings

from django import forms

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
        help_text="ID of the PyLucid Admin Design.")

    lang_code = forms.ChoiceField(
        choices=Language.objects.values_list('code', 'description'),
        initial=Language.objects.all()[0].code,
        help_text="Default language")

    class Meta:
        app_label = 'pylucid'
