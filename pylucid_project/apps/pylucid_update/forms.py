# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import Language

class UpdateForm(forms.Form):
    language = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        help_text=_("Select the language of your existing page data."),
    )
