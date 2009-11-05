# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from pylucid_project.utils.site_utils import SitePreselectPreference

from dbpreferences.forms import DBPreferencesBaseForm


class BlogPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    class Meta:
        app_label = 'blog'
