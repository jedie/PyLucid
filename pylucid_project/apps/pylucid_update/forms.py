# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import Language

class UpdateForm(forms.Form):
    language = forms.ModelChoiceField(
        queryset=Language.on_site.all(),
        help_text=_("Select the language of your existing page data."),
    )


class ConfirmField(forms.Field):
    def clean(self, value):
        if value != "yes":
            raise forms.ValidationError("You must insert 'yes' to confirm!")
        return value # return the cleaned data.

class WipeSiteConfirm(forms.Form):
    confirm = ConfirmField(help_text=_("Please insert 'yes' to confirm."))
