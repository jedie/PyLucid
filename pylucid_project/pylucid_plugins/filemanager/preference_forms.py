# coding: utf-8

from django.utils.translation import ugettext_lazy as _

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid_project.utils.site_utils import SitePreselectPreference


class FilemanagerPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    """
    Don't know what we can setup here, yet
    """

    class Meta:
        app_label = 'filemanager'
