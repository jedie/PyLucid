# coding: utf-8

"""
    PyLucid i18n tools
    ~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev:$"

from xml.sax.saxutils import escape

from django.conf import settings
from django.utils import translation
from django.http import HttpResponseRedirect

from pylucid.models import Language


def reset_language_settings(request):
    """
    Reset the favored language information.
    -Remove language information from session
    -Delete djangos language cookie
    """
    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg.green("reset the favored language information.")

    if "django_language" in request.session:
        # Remove language information from session.
        del(request.session["django_language"])
        request.session.modified = True

    response = HttpResponseRedirect(request.path)
    # Delete djangos language cookie.
    response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)
    return response


def setup_language(request):
    """
    Add the Language model entry to request.PYLUCID.lang_entry.
    Use the django language information
    from django local middleware, see: http://docs.djangoproject.com/en/dev/topics/i18n/#id2 
    """
    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg("settings.PYLUCID.I18N_DEBUG:")
        
        key = "HTTP_ACCEPT_LANGUAGE"
        request.page_msg("%s:" % key, request.META.get(key, '---'))
        
        key = settings.LANGUAGE_COOKIE_NAME
        request.page_msg("cookie %r:" % key, request.COOKIES.get(key, "---"))
        
        request.page_msg("session 'django_language':", request.session.get('django_language', "---"))
        
    # Use language infomation from django locale middleware
    lang_code = request.LANGUAGE_CODE
    activate_lang(request, lang_code, from_info="request.LANGUAGE_CODE")
    
    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg("request.PYLUCID.default_lang_code:", request.PYLUCID.default_lang_code)
        request.page_msg("request.PYLUCID.default_lang_entry:", request.PYLUCID.default_lang_entry)
        request.page_msg("request.PYLUCID.lang_entry:", request.PYLUCID.lang_entry)


def activate_lang(request, lang_code, from_info, save=False):
    """
    Try to use the given lang_code. If not exist fall back to lang from system preferences.
    Add the Language model entry to request.PYLUCID.lang_entry
    """
    lang_codes = [lang_code]
    if "-" in lang_code:
         lang_codes += lang_code.split("-")
    
    lang_entry = None
    tried_codes = []
    for code in lang_codes:
        try:
            lang_entry = Language.objects.get(code=code)
            break
        except Language.DoesNotExist:
            tried_codes.append(code)
    
    if tried_codes and (settings.DEBUG or settings.PYLUCID.I18N_DEBUG):
        request.page_msg.red(
            "debug: Favored language %r (from: %s) doesn't exist." % (tried_codes, from_info)
        )
    
    if not lang_entry:
        # The favored language doesn't exist -> use default lang from preferences
        lang_entry = request.PYLUCID.default_lang_entry
        lang_code = request.PYLUCID.default_lang_code
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.green("Use default language %r (from preferences)" % lang_entry)
    else:
        # lang entry found
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.green("Use language %r (from: %s)" % (code, from_info))
        if save:
            # Save language in session for next requests
            if settings.PYLUCID.I18N_DEBUG:
                request.page_msg("Save lang code %r into request.session['django_language']" % code)
            request.session["django_language"] = code
      
    translation.activate(code) # activate django i18n
    request.LANGUAGE_CODE = code
    request.PYLUCID.lang_entry = lang_entry