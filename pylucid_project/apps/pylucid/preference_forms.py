# coding: utf-8

from django import forms

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid.models import Language

class SystemPreferencesForm(DBPreferencesBaseForm):
    """ test preferences form """
    lang_code = forms.ChoiceField(
        choices=Language.objects.values_list('code', 'description'),
        initial=Language.objects.all()[0].code,
        help_text="Default language")

    class Meta:
        app_label = 'pylucid'