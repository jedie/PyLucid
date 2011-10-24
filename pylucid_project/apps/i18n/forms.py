# coding: utf-8

"""
    i18n forms
    ~~~~~~~~~~~

    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import forms


class LanguageSelectForm(forms.Form):
    language = forms.ChoiceField()

    def __init__(self, languages, *args, **kwargs):
        """ Change form field data in a DRY way """
        super(LanguageSelectForm, self).__init__(*args, **kwargs)
        self.fields['language'].choices = [(lang.code, lang.description) for lang in languages]
