# coding: utf-8

"""
    PyLucid include plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import time
import traceback

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from django_tools.utils.http import HttpRequest

from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.apps.pylucid.markup import MARKUP_DATA
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.markup.hightlighter import make_html
from pylucid_project.pylucid_plugins.include.preference_forms import PreferencesForm
from pylucid_project.utils.escape import escape




MARKUPS = dict(tuple([(data[1], data[0]) for data in MARKUP_DATA]))



def _error(request, msg, staff_msg):
    etype, value, tb = sys.exc_info()
    if tb is not None:
#        if settings.DEBUG and settings.RUN_WITH_DEV_SERVER:
#            raise
        if request.user.is_superuser:
            # put the full traceback into page_msg, but only for superusers
            messages.debug(request,
                mark_safe(
                    "%s:<pre>%s</pre>" % (escape(staff_msg), escape(traceback.format_exc()))
                )
            )
            return

    if request.user.is_staff:
        messages.error(request, staff_msg)

    return "[%s]" % msg


def _render(request, content, path_or_url, markup, highlight, strip_html):
    markup_no = None
    if markup:
        if markup not in MARKUPS:
            return _error(request, "Include error.",
                "Can't include: Unknown markup %r (Available: %s)" % (markup, ", ".join(MARKUPS.keys()))
            )
        markup_no = MARKUPS[markup]

    if markup_no:
        content = apply_markup(content, markup_no, request, escape_django_tags=False) # xxx: escape_django_tags
        if highlight == True:
            highlight = "html"

    if highlight == True:
        highlight = os.path.splitext(path_or_url)[1]

    if highlight is not None:
        content = make_html(content, highlight)

    if not (markup_no or highlight):
        if strip_html:
            content = strip_tags(content)
        content = escape(content)

    return content


def local_file(request, filepath, encoding="utf-8", markup=None, highlight=None, strip_html=True):
    """
    include a local files from filesystem into a page.
    Arguments, see DocString of lucidTag()
    """
    filepath = os.path.normpath(os.path.abspath(filepath))

    # include local files only, if it stored under this path:
    basepath = getattr(settings, "PYLUCID_INCLUDE_BASEPATH", None)
    if not basepath:
        return _error(request, "Include error.", "settings.PYLUCID_INCLUDE_BASEPATH not set!")
    
    basepath = os.path.normpath(basepath)
    if not filepath.startswith(basepath):
        return _error(request, "Include error.", "Filepath doesn't start with %r" % basepath)

    try:
        f = file(filepath, "r")
        content = f.read()
        f.close()

        content = unicode(content, encoding)
    except Exception, err:
        return _error(request, "Include error.", "Can't read file %r: %s" % (filepath, err))

    return _render(request, content, filepath, markup, highlight, strip_html)


@render_to()#, debug=True)
def remote(request, url, encoding=None, markup=None, highlight=None, strip_html=True, **kwargs):
    """
    include a remote file into a page.
    Arguments, see DocString of lucidTag()
    """
    # Get preferences from DB and overwrite them
    pref_form = PreferencesForm()
    preferences = pref_form.get_preferences(request, lucidtag_kwargs=kwargs)

    cache_key = "include_remote_%s" % url
    context = cache.get(cache_key)
    if context:
        from_cache = True
    else:
        from_cache = False

        # Get the current page url, for referer
        context = request.PYLUCID.context
        page_absolute_url = context["page_absolute_url"]
        current_language = request.PYLUCID.current_language
        current_language_code = current_language.code

        socket_timeout = preferences["socket_timeout"]
        user_agent = preferences["user_agent"]

        start_time = time.time()
        try:
            # Request the url content in unicode
            r = HttpRequest(url, timeout=socket_timeout, threadunsafe_workaround=True)
            r.request.add_header("User-agent", user_agent)
            r.request.add_header("Referer", page_absolute_url)
            r.request.add_header("Accept-Language", current_language_code)

            response = r.get_response()
            raw_content = r.get_unicode()
        except Exception, err:
            return _error(request, "Include error.", "Can't get %r: %s" % (url, err))

        duration = time.time() - start_time

        # get request/response information
        request_header = response.request_header
        response_info = response.info()

        context = {
            "raw_content": raw_content,
            "request_header": request_header,
            "response_info": response_info,
            "duration": duration,
        }
        cache.set(cache_key, context , preferences["cache_timeout"])

    content = context["raw_content"]
    content = _render(request, content, url, markup, highlight, strip_html)

    context.update({
        "template_name": preferences["remote_template"],
        "url": url,
        "content": content,
        "from_cache": from_cache,
        "preferences": preferences,
    })
    return context


def lucidTag(request, **kwargs):
    """
    include a local file or a remote page into CMS page.
    
    Shared arguments for include.local_file and include.remote:
    |= parameter |= default |= description
    | encoding   | "utf-8"  | content charset
    | markup     | None     | Name of the Markup to apply (e.g.: "creole", "rest")
    | highlight  | None     | File extensions for pygments or True for autodetection (e.g.: "py", "html+django")
    | strip_html | True     | Cut html tags out from content?
    
    You can combine markup and highlight. Result is pygmentised html code ;)
    if not markup and not highlight, the result would be strip_html (optional) and then escaped.
    
    Optional arguments for include.remote to overwrite preferences:
    |= parameter      |= description
    | remote_template | template filename for render the result
    | socket_timeout  | socket timeout in seconds for getting remote data
    | cache_timeout   | number of seconds to cache remote data
    
    example:
    
    {% lucidTag include.local_file filepath="README.creole" markup="creole" %}
    {% lucidTag include.remote url="http://domain.tld/foobar.py" highlight="py" %}
    """
    return _error(request, "Include error.",
        "Wrong lucidTag Syntax:"
        " You must use {% lucidTag include.local_file ... %} or {% lucidTag include.remote ... %} !"
    )
