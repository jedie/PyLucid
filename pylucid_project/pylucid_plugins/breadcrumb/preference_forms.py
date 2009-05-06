# coding: utf-8

from django import forms
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm


class BreadcumbPrefForm(DBPreferencesBaseForm):
    separator = forms.CharField(
        initial = _(u" \u00BB "),
        help_text = _('Seperator between every breadcrumb link'),
    )
    print_last_page = forms.BooleanField(
        initial = True, required=False,
        help_text = _(
            "If checked the actual page will be the last page in the bar."
            " Otherwise the parentpage."
        ),
    )
    print_index = forms.BooleanField(
        initial = True, required=False,
        help_text = _('If checked every back link bar starts with a link to "index_url"'),
    )
    index_url = forms.CharField(
        initial = "/",
        help_text = _("The url used for print_index. Note: not verify if the url exists."),
    )
    index = forms.CharField(
        initial = _("Index"),
        help_text = _('the name that is printed for the indexpage'),
    )

    class Meta:
        app_label = 'breadcrumb'