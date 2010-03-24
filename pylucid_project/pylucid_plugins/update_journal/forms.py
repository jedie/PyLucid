# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _


class CleanupUpdateJournalForm(forms.Form):
    LAST_NUMBERS = "n"
    LAST_DAYS = "d"
    LAST_HOURS = "h"

    TYPE_CHOICES = (
        (LAST_NUMBERS, _("keep the last X entries")),
        (LAST_DAYS, _("keep entries from the last X days")),
        (LAST_HOURS, _("keep entries from the last X hours")),
    )
    number = forms.IntegerField(initial=7, min_value=0, help_text=_("Number of entries to be retained."))
    delete_type = forms.ChoiceField(initial=LAST_DAYS, choices=TYPE_CHOICES,
        help_text=_("Witch 'retained' type is the given number?")
    )
    limit_site = forms.BooleanField(initial=True, required=False,
        help_text=_("Limit the query to the current site?")
    )
