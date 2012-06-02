# coding: utf-8


"""
    PyLucid i18n tools
    ~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""


if __name__ == "__main__":
    # For doctest only
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import translation

from pylucid_project.apps.pylucid.models import Language


def change_url_language(old_url, new_lang_code):
    """
    >>> change_url_language("/en/foo/bar/", "de")
    '/de/foo/bar/'
    >>> change_url_language("/en/", "de")
    '/de/'
    >>> change_url_language("/", "de")
    '/de/'
    >>> change_url_language("/en/?foo=bar", "de")
    '/de/?foo=bar'
    """
#    print "old_url: %r" % old_url
    url = old_url.lstrip("/")
    if not url:
        return "/%s/" % new_lang_code

    url = url.split("/", 1)[1]
#    print "url: %r" % url
    new_url = "/%s/%s" % (new_lang_code, url)
#    print "new_url: %r" % new_url
    return new_url


def change_url(request, new_lang_code, save_get_parameter=True):
    """
    change the language code in the current url
    
    if save_get_parameter==True:
        keep GET parameter in url
    else:
        remove GET parameter
    """
    if save_get_parameter:
        old_url = request.get_full_path()
    else:
        old_url = request.path

    return change_url_language(old_url, new_lang_code)


def get_url_language(request, url=None):
    """
    return the language instance based on the language code in the url.
    If url==None: use the current request.path.
    """
    if url is None:
        url = request.path

    url = url.lstrip("/")
    language_code = url.split("/", 1)[0]
    for language in request.PYLUCID.languages:
        if language_code == language.code:
            return language


def reset_language_settings(request):
    """
    Reset the favored language information.
    -Remove language information from session
    -Delete djangos language cookie
    """
    if settings.PYLUCID.I18N_DEBUG:
        messages.success(request,
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

    if settings.PYLUCID.I18N_DEBUG:
        messages.info(request, "settings.PYLUCID.I18N_DEBUG:")
        key = "HTTP_ACCEPT_LANGUAGE"
        messages.info(request, "%s: %r" % (key, request.META.get(key, '---')))
        key = settings.LANGUAGE_COOKIE_NAME
        messages.info(request, "request.PYLUCID.languages: %r" % request.PYLUCID.languages)
        messages.info(request, "request.session['django_language']: %r" % request.session.get('django_language', "---"))
        messages.info(request, "request.LANGUAGE_CODE: %r (set in django.middleware.local)" % lang_code)

    current_language = request.PYLUCID.current_language
    activate_language(request, lang_entry=current_language)

#    lang_entry = Language.objects.get_from_code(request, lang_code)
#    if lang_entry is None:
#        if settings.PYLUCID.I18N_DEBUG:
#            messages.error(request, 
#                'Favored language "%s" does not exist -> use activate_default_language()' % lang_code
#            )
#        activate_default_language(request)
#    else:
#        activate_language(request, lang_entry)


def activate_default_language(request):
    """ activate default lang from preferences """
    default_language = request.PYLUCID.default_language

    if settings.PYLUCID.I18N_DEBUG:
        messages.success(request, 'Use default language "%s"' % default_language.code)

    activate_language(request, default_language)


def activate_language(request, lang_entry, save=False):
    """
    Activate django i18n language and set some request objects:
    
         * request.PYLUCID.current_language
    Add lang_entry witch is the given Language model instance.
        
        * request.LANGUAGE_CODE
    Set LANGUAGE_CODE from django.middleware.locale.LocaleMiddleware
    see: http://docs.djangoproject.com/en/dev/topics/i18n/
    """
    if save:
        # Save language in session for next requests
        if settings.PYLUCID.I18N_DEBUG:
            messages.info(request,
                'Save lang code "%s" into request.session[\'django_language\']' % lang_entry.code
            )
        request.session["django_language"] = lang_entry.code

    if request.LANGUAGE_CODE == lang_entry.code:
        # this language is active, nothing to do
        if settings.PYLUCID.I18N_DEBUG:
            messages.info(request,
                "Activation language %r not needed: It's the current used language." % lang_entry.code
            )
        return

    request.LANGUAGE_CODE = lang_entry.code
    request.PYLUCID.current_language = lang_entry

    # activate django i18n:
    translation.activate(lang_entry.code)
    request.LANGUAGE_CODE = translation.get_language()
    if settings.DEBUG or settings.PYLUCID.I18N_DEBUG:
        if lang_entry.code != request.LANGUAGE_CODE:
            messages.error(
                request, 'Language "%s" was not activated from django! Fallback to "%s"' % (
                lang_entry.code, request.LANGUAGE_CODE)
            )
        elif settings.PYLUCID.I18N_DEBUG:
            messages.success(request, 'Language "%s" activated successfuly.' % lang_entry.code)


def assert_language(request, language, save_get_parameter=False, check_url_language=False):
    """
    return a redirect url if the current used language is not the same as the given one.
    This is useful in plugins e.g.: in the blog detail view
    """
    new_url = None

    if language != request.PYLUCID.current_language:
        if settings.PYLUCID.I18N_DEBUG:
            messages.info(request, "entry language %s is not %s" % (language, request.PYLUCID.current_language))

        activate_language(request, language, save=True)

        # change only the lang code in the url:
        new_url = change_url(request, language.code, save_get_parameter)

    if check_url_language:
        url_language = get_url_language(request)
        if url_language != language:
            # The url contains the wrong language code -> redirect to the right one
            new_url = change_url(request, language.code, save_get_parameter)

    if new_url:
        if new_url != request.path:
            # redirect, so the new selected language would be used
            return new_url
        else:
            msg = "FIXME: Redirect loop! new url: %r" % new_url
            if settings.DEBUG or request.user.is_staff:
                messages.error(request, msg)


def resort_languages(request, url_lang_code):
    """
    Put the language from the url to the first language.
    """
    if request.PYLUCID.languages[0].code == url_lang_code:
        if settings.PYLUCID.I18N_DEBUG:
            messages.info(request, "no need to resort languages: first language == url language code.")
        return

    for no, lang in enumerate(request.PYLUCID.languages):
        if lang.code == url_lang_code:
            url_lang = request.PYLUCID.languages.pop(no)
            request.PYLUCID.languages.insert(0, url_lang)
            if settings.PYLUCID.I18N_DEBUG:
                messages.info(request, "move language %r (from url code) to first." % url_lang)
            return



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
