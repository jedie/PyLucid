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

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

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
        request.page_msg.successful("reset the favored language information.")

    if "django_language" in request.session:
        # Remove language information from session.
        del(request.session["django_language"])
        request.session.modified = True

    response = HttpResponseRedirect(request.path)
    # Delete djangos language cookie.
    response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)
    return response


#def setup_language(request, lang_entry):
#    """
#    Add the Language model entry to request.PYLUCID.lang_entry.
#    Use the django language information
#    from django local middleware, see: http://docs.djangoproject.com/en/dev/topics/i18n/#id2 
#    """
##    if settings.PYLUCID.I18N_DEBUG:
##        request.page_msg("settings.PYLUCID.I18N_DEBUG:")
##        
##        request.page_msg("url_lang_code: %r" % url_lang_code)
##        
##        key = "HTTP_ACCEPT_LANGUAGE"
##        request.page_msg("%s:" % key, request.META.get(key, '---'))
##        
##        key = settings.LANGUAGE_COOKIE_NAME
##        request.page_msg("cookie %r:" % key, request.COOKIES.get(key, "---"))
##        
##        request.page_msg("session 'django_language':", request.session.get('django_language', "---"))
#       
#    if url_lang_code != None:
#        # Use the language code from the url
#        try:
#            lang_entry = Language.objects.get(code=url_lang_code)
#        except Language.DoesNotExist:
#            # fall back to default 
#        
#    activate_language(request, lang_entry)
#    
#    if settings.PYLUCID.I18N_DEBUG:
#        request.page_msg("request.PYLUCID.default_lang_code:", request.PYLUCID.default_lang_code)
#        request.page_msg("request.PYLUCID.default_lang_entry:", request.PYLUCID.default_lang_entry)
#        request.page_msg("request.PYLUCID.lang_entry:", request.PYLUCID.lang_entry)

#def split_lang_codes(raw_lang_codes):
#    """
#    >>> split_lang_codes("de-AT")
#    ['de', 'AT']
#    >>> split_lang_codes(["en", "de-AT"])
#    ['en', 'de', 'AT']
#    """
#    if isinstance(raw_lang_codes, basestring):
#        raw_lang_codes = [raw_lang_codes]
#    
#    assert isinstance(raw_lang_codes, list)
#    
#    lang_codes = []
#    for code in raw_lang_codes:
#        if "-" in code:
#            lang_codes += code.split("-")
#        else:
#            lang_codes.append(code)
#    return lang_codes

def activate_auto_language(request):
    """
    Activate language via auto detection.
    
    Use request.LANGUAGE_CODE from django locale middleware. If this language
    doesn't exist -> fall back to language set in system preferences.
    
    FIXME: We must use the client list from request.META['HTTP_ACCEPT_LANGUAGE']
        The PyLucid admin can setup a language witch doesn't exist in django MO files. 
    """
    lang_code = request.LANGUAGE_CODE
    try:
        lang_entry = Language.objects.get(code=lang_code)
    except Language.DoesNotExist:
        activate_default_language(request)
    else:
        activate_language(request, lang_entry)
        

def activate_default_language(request):
    """ activate default lang from preferences """
    lang_entry = request.PYLUCID.default_lang_entry

    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg.successful("Use default language %r (from preferences)" % lang_entry.code)
        
    activate_language(request, lang_entry)


def activate_language(request, lang_entry, save=False):
    """
    Activate django i18n language and set some request objects:
    
         * request.PYLUCID.lang_entry
    Add lang_entry witch is the given Language model instance.
        
        * request.LANGUAGE_CODE
    Set LANGUAGE_CODE from django.middleware.locale.LocaleMiddleware
    see: http://docs.djangoproject.com/en/dev/topics/i18n/
    """
    request.LANGUAGE_CODE = lang_entry.code   
    request.PYLUCID.lang_entry = lang_entry

    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg.successful("Activate language %r" % lang_entry.code)
        
    if save:
        # Save language in session for next requests
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg("Save lang code %r into request.session['django_language']" % lang_entry.code)
        request.session["django_language"] = lang_entry.code
      
    # activate django i18n:
    translation.activate(lang_entry.code) 




class UrlLangCodeWrong(Exception):
    """ Would be raused, if the url code in the url doesn't exist """
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."