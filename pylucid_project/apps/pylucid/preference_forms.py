# coding: utf-8

from django import forms

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid.models import Language

if Language.objects.count() == 0:
    # FIXME: Insert first language
    Language(code="en", description="english").save()


class SystemPreferencesForm(DBPreferencesBaseForm):
    """ test preferences form """
    lang_code = forms.ChoiceField(
        choices=Language.objects.values_list('code', 'description'),
        initial=Language.objects.all()[0].code,
        help_text="Default language")

    class Meta:
        app_label = 'pylucid'