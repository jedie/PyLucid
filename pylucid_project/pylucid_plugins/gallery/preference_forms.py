# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.site_utils import SitePreselectPreference

from dbpreferences.forms import DBPreferencesBaseForm
from django_tools.fields import SignSeparatedField


class GalleryPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    unauthorized_signs = forms.CharField(
        initial=".. // \\",
        help_text=_(
            "raise 500 if one of the signs in the path (separated by spaces!)"
        ),
    )
    class Meta:
        app_label = 'gallery'
