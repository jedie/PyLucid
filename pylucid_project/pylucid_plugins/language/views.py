# coding: utf-8

"""
    PyLucid language tools
    ~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev:$"

from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid.system import i18n
from pylucid.models import Language
from pylucid.decorators import render_to

from language.preference_forms import LanguagePrefForm

RESET_KEY = "reset"

@render_to("language/language_selector.html")
def lucidTag(request):
    """ insert language selector list into page """

    # Get preferences
    pref_form = LanguagePrefForm()
    pref_data = pref_form.get_preferences()

    current_pagetree = request.PYLUCID.pagetree
    absolute_url = current_pagetree.get_absolute_url()
    current_url = absolute_url.strip("/") # For {% url ... %}

    existing_languages = Language.objects.all()
    context = {
        "current_url": current_url,
        "existing_languages": existing_languages,
        "add_reset_link": pref_data["add_reset_link"],
        "reset_key": RESET_KEY,
    }
    return context



def http_get_view(request):
    lang_code = request.GET.get("language", False)
    if not lang_code:
        return
    elif lang_code == RESET_KEY:
        # We should reset the favored language settings
        response = i18n.reset_language_settings(request)
        return response

    i18n.activate_lang(request, lang_code, from_info="GET parameter", save=True)

    # redirect, so the new selected language would be used
    return HttpResponseRedirect(request.path)
