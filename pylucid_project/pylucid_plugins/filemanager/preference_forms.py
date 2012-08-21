# coding: utf-8

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid_project.utils.site_utils import SitePreselectPreference


class FilemanagerPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    """
    Don't know what we can setup here, yet
    """
    class Meta:
        app_label = 'filemanager'
