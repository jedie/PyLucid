# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from django_tools.fields.sign_separated import SignSeparatedFormField

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid_project.utils.site_utils import SitePreselectPreference


class GalleryPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    unauthorized_signs = SignSeparatedFormField(
        separator=" ", initial=".. // \\",
        help_text=_(
            "raise 500 if one of the signs in the path (separated by spaces!)"
        ),
    )
    class Meta:
        app_label = 'gallery'
