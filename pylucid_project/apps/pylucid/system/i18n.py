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

__version__ = "$Rev:$"


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
        request.page_msg.successful(
            "Reset the favored language information. (Delete session and cookie entry.)"
        )

    if "django_language" in request.session:
        # Remove language information from session.
        del(request.session["django_language"])
        request.session.modified = True

    response = HttpResponseRedirect(request.path)
    # Delete djangos language cookie.
    response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)
    return response


def activate_auto_language(request):
    """
    Activate language via auto detection.
    
    Use request.LANGUAGE_CODE from django locale middleware. If this language
    doesn't exist -> fall back to language set in system preferences.
    
    FIXME: We must use the client list from request.META['HTTP_ACCEPT_LANGUAGE']
        The PyLucid admin can setup a language witch doesn't exist in django MO files. 
    """
    lang_code = request.LANGUAGE_CODE
    if "-" in lang_code:
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg("Use only the first part of %r (from request.LANGUAGE_CODE)." % lang_code)
        lang_code = lang_code.split("-")[0]

    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg("settings.PYLUCID.I18N_DEBUG:")
        key = "HTTP_ACCEPT_LANGUAGE"
        request.page_msg("%s: %r" % (key, request.META.get(key, '---')))
        key = settings.LANGUAGE_COOKIE_NAME
        request.page_msg("cookie %r: %r" % (key, request.COOKIES.get(key, "---")))
        request.page_msg("session 'django_language': %r" % request.session.get('django_language', "---"))
        request.page_msg("request.LANGUAGE_CODE: %r (set in django.middleware.local)" % lang_code)

    try:
        lang_entry = Language.objects.get(code=lang_code)
    except Language.DoesNotExist:
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg.error(
                'Favored language "%s" does not exist -> use activate_default_language()' % lang_code
            )
        activate_default_language(request)
    else:
        activate_language(request, lang_entry)


def activate_default_language(request):
    """ activate default lang from preferences """
    lang_entry = Language.objects.get_default()

    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg.successful('Use default language "%s"' % lang_entry.code)

    activate_language(request, lang_entry)


def activate_language(request, lang_entry, save=False):
    """
    Activate django i18n language and set some request objects:
    
         * request.PYLUCID.language_entry
    Add lang_entry witch is the given Language model instance.
        
        * request.LANGUAGE_CODE
    Set LANGUAGE_CODE from django.middleware.locale.LocaleMiddleware
    see: http://docs.djangoproject.com/en/dev/topics/i18n/
    """
    request.LANGUAGE_CODE = lang_entry.code
    request.PYLUCID.language_entry = lang_entry

    if settings.PYLUCID.I18N_DEBUG:
        request.page_msg.successful('Activate language "%s"' % lang_entry.code)

    if save:
        # Save language in session for next requests
        if settings.PYLUCID.I18N_DEBUG:
            request.page_msg(
                'Save lang code "%s" into request.session[\'django_language\']' % lang_entry.code
            )
        request.session["django_language"] = lang_entry.code

    # activate django i18n:
    translation.activate(lang_entry.code)




if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
