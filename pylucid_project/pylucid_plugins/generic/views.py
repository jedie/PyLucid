# coding: utf-8

"""
    Generic plugin
    ~~~~~~~~~~~~~~
    
    Simple rendering templates with some variables.

    :copyleft: 2010-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import datetime
import sys
import time
import traceback

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.utils import simplejson as json
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project import VERSION_STRING
from pylucid_project.utils.escape import escape

from django_tools.utils.http import HttpRequest



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
        return "[%s]" % msg

    if request.user.is_staff:
        messages.error(request, staff_msg)

    return "[%s]" % msg


def get_json_remote(request, url, cache_time, timeout, encoding=None):
    """
    include a remote file into a page.
    Arguments, see DocString of lucidTag()
    """
    cache_key = "get_json_remote_%s" % url
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

        user_agent = "PyLucid CMS v%s" % VERSION_STRING

        start_time = time.time()
        try:
            # Request the url content in unicode
            r = HttpRequest(url, timeout=timeout, threadunsafe_workaround=True)
            r.request.add_header("User-agent", user_agent)
            r.request.add_header("Referer", page_absolute_url)
            r.request.add_header("Accept-Language", current_language_code)

            response = r.get_response()
            raw_content = r.get_unicode()
        except Exception, err:
            return _error(request, "Remote error.", "Can't get %r: %s" % (url, err))

        duration = time.time() - start_time

        # get request/response information
        request_header = response.request_header
        response_info = response.info()

        raw_json = raw_content[len("jsonFlickrFeed("):-1]
        try:
            data = json.loads(raw_json)
        except Exception, err:
            _error(request, "Remote error.", "Can't load json %r: %s" % (url, err))
            data = None
        else:
            # Insert alternate picture sizes
            for pic in data["items"]:
                url = pic["media"][u"m"]
                for char in (u"s", u"q", u"t", u"n", u"z", u"c", u"b"):
                    if not char in pic["media"]:
                        pic["media"][char] = url.replace(u"_m.jpg", u"_%s.jpg" % char)

            # separate description text
            for pic in data["items"]:
                raw_desc = pic["description"]
                desc = raw_desc.rsplit(u"</a></p>", 1)[1].strip()
                # Cleanup:
                desc = "<br />".join([txt.strip() for txt in desc.split("<br />") if txt.strip()])
                pic["desc_text"] = desc

            # Parse the 'date_taken' time without local information
            for pic in data["items"]:
                raw_date = pic["date_taken"]
                dt = raw_date.rsplit("-", 1)[0]
                dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                pic["datetime"] = dt

        context = {
            "url": url,
            "raw_content": raw_content,
            "data":data,
            "request_header": request_header,
            "response_info": response_info,
            "duration": duration,
            "cache_time":cache_time,
            "timeout": timeout,
        }
        cache.set(cache_key, context, cache_time)

    context["from_cache"] = from_cache
    return context


@render_to()
def flickr_rss(request, id=None, template_name="generic/flickr_colorbox.html", max=None, cache_time=60, timeout=5, debug=False, **kwargs):
    url = "https://secure.flickr.com/services/feeds/photos_public.gne?format=json"
    if id:
        url += "&id=%s" % id

    current_language = request.PYLUCID.current_language
    current_language_code = current_language.code
    url += "&lang=%(l)s-%(l)s" % {"l":current_language_code}

    context = get_json_remote(request, url, cache_time, timeout)
    if isinstance(context, basestring):
        # Error message
        return context

    if max and context["data"]:
        context["data"]["items"] = context["data"]["items"][:max]

    context.update({
        "template_name":template_name,
        "max": max,
        "debug": debug,
    })
    context.update(kwargs)
    return context


@render_to()
def youtube(request, id, width=640, height=505, template_name="generic/YouTube.html", **kwargs):
    context = {
        "id": id,
        "width": width,
        "height": height,
        "template_name":template_name,
    }
    context.update(kwargs)
    return context


@render_to()
def ohloh(request, project, js_file="project_thin_badge.js", template_name="generic/ohloh.html", **kwargs):
    context = {
        "project": project,
        "js_file": js_file,
        "template_name":template_name,
    }
    context.update(kwargs)
    return context


@render_to()
def lucidTag(request, **context):
    """
    Generic plugin for inserting external widgets.
    
    Available boilerplate:
    * YouTube
    * ohloh
    * flickr
    
    more info:
    http://www.pylucid.org/permalink/360/generic-plugin
    
    example:
        {% lucidTag generic.youtube id="XL1UNmLDLKc" %}
        {% lucidTag generic.youtube id="XL1UNmLDLKc" width=960 height=745 %}
        {% lucidTag generic.ohloh project="pylucid" %}
        {% lucidTag generic.ohloh project="python" js_file="project_users.js?style=rainbow" %}
        {% lucidTag generic.flickr_rss %}
        {% lucidTag generic.flickr_rss id="12345678@N90" max=5 %}
        {% lucidTag generic template_name="myowntemplate.html" %}
    """
    if "template_name" not in context and (request.user.is_staff or settings.DEBUG):
        messages.info(request, _("At least you must add template_name argument to {% lucidTag generic %} !"))
    else:
        return context
