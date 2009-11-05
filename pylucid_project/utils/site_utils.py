# coding: utf-8

"""
    Simple helper for site preselection
    
    used in pylucid plugins e.g.: lexicon, blog
"""

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _


def get_site_preselection(pref_form, request):
    """
    Get the form init value for a M2M to site for preselecting it.
    """
    pref_data = pref_form.get_preferences()
    preselect = pref_data["site_preselection"]

    if preselect == pref_form.PRESELECT_ALL:
        # Preselect all accessible sites
        user_profile = request.user.get_profile()
        # All accessible sites from the current user:
        return user_profile.sites.values_list('id', flat=True)
    elif preselect == pref_form.PRESELECT_CURRENT:
        # Preselect the current site only
        return [Site.objects.get_current().pk]

    # Do not preselect the site
    return []


class SitePreselectPreference(forms.Form):
    """
    Usage in a DBPreferencesBaseForm 
    """
    PRESELECT_NONE = "N"
    PRESELECT_CURRENT = "C"
    PRESELECT_ALL = "A"

    PRESELECT_CHOICES = (
        (PRESELECT_NONE, _("No site")),
        (PRESELECT_CURRENT, _("current site")),
        (PRESELECT_ALL, _("all accessable sites")),
    )
    PRESELECT_DICT = dict(PRESELECT_CHOICES)

    site_preselection = forms.ChoiceField(choices=PRESELECT_CHOICES,
        help_text=_("Witch site(s) sould be preselected if you create a new entry?"),
        initial=PRESELECT_ALL,
    )
