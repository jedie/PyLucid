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

__version__= "$Rev:$"

from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid.system import i18n
from pylucid.models import Language

RESET_KEY = "reset"

def lucidTag(request):
    """ insert language selector list into page """
    existing_languages = Language.objects.all()
    context = {
        "existing_languages": existing_languages,
        "debug": (settings.DEBUG or settings.PYLUCID.I18N_DEBUG),
        "reset_key": RESET_KEY,
    }
    return render_to_response('language/language_selector.html', context, 
        context_instance=RequestContext(request)
    )


def html_get_view(request):
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
    