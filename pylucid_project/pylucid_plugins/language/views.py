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
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from pylucid.system import i18n
from pylucid.models import PageMeta, Language
from pylucid.decorators import render_to

from language.preference_forms import LanguagePrefForm

RESET_KEY = "reset"

@render_to("language/language_selector.html")
def lucidTag(request):
    """ insert language selector list into page """

    # Get preferences
    pref_form = LanguagePrefForm()
    pref_data = pref_form.get_preferences()

    current_lang = request.PYLUCID.lang_entry

    current_pagetree = request.PYLUCID.pagetree
    absolute_url = current_pagetree.get_absolute_url()
    current_url = absolute_url.strip("/") # For {% url ... %}

    existing_languages = Language.objects.all()
    context = {
        "current_lang": current_lang,
        "current_url": current_url,
        "existing_languages": existing_languages,
        "add_reset_link": pref_data["add_reset_link"],
        "reset_key": RESET_KEY,
    }
    return context



def http_get_view(request):
    """
    Switch the client favored language and save it for every later requests.
    """
    raw_lang_code = request.GET.get("language", False)
    if not raw_lang_code:
        return

    if len(raw_lang_code) != 2:
        return

    if raw_lang_code == request.LANGUAGE_CODE:
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error("No language switch needed.")
        return

    try:
        lang_entry = Language.objects.get(code=raw_lang_code)
    except Language.DoesNotExist, err:
        if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error("Wrong lang code in get parameter: %s" % err)
        return

    i18n.activate_language(request, lang_entry, save=True)

    current_pagemeta = request.PYLUCID.pagemeta
    if current_pagemeta.lang == lang_entry:
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error("Current page is in right language. No redirect needed.")
        return

    pagetree = request.PYLUCID.pagetree
    try:
        pagemeta = PageMeta.objects.get(page=pagetree, lang=lang_entry)
    except PageMeta.DoesNotExist, err:
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error("PageMeta doesn't exist in lang %r. So no redirect needed." % lang_entry)
        return

    url = pagemeta.get_absolute_url()

    # redirect, so the new selected language would be used
    return HttpResponseRedirect(url)
