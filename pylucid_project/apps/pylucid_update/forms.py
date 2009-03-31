# coding: utf-8

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.models import Language

class UpdateForm(forms.Form):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        help_text=_("Select the site for the existing pages."),
    )
    language = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        help_text=_("Select the language of your existing page data."),
    )
