#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid.index
    ~~~~~~~~~~~~~

    - Display a PyLucid CMS Page
    - Answer a _command Request

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import datetime, md5

from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template import RequestContext
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings

from PyLucid import models

from PyLucid.system import plugin_manager
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.exceptions import AccessDenied
from PyLucid.system.page_msg import PageMessages
from PyLucid.system.detect_page import get_current_page_obj, \
                                                            get_default_page_id
from PyLucid.system.URLs import URLs
from PyLucid.system.context_processors import add_dynamic_context, add_css_tag
from PyLucid.system.utils import setup_debug
from PyLucid.tools.content_processors import apply_markup, \
                                    render_string_template, redirect_warnings
from PyLucid.tools.utils import escape, escape_django_tags
from PyLucid.plugins_internal.page_style.page_style import replace_add_data


def _render_cms_page(request, context, page_content=None):
    """
    render the cms page.
    - render a normal cms request
    - render a _command request: The page.content is the output from the plugin.
    """
    if request.anonymous_view == False:
        # context["robots"] was set in contex_processors.static()
        # Hide the response from search engines
        context["robots"] = "NONE,NOARCHIVE"

    current_page = context["PAGE"]

    if page_content:
        # The page content comes e.g. from the _command plugin
#        current_page.content = page_content
        page_content = escape_django_tags(page_content)
    else:
        # get the current page data from the db
        page_content = current_page.content

        markup_object = current_page.markup
        page_content = apply_markup(page_content, context, markup_object)

    # Render only the CMS page content:
    page_content = render_string_template(page_content, context)

    # http://www.djangoproject.com/documentation/templates_python/#filters-and-auto-escaping
    page_content = mark_safe(page_content) # turn djngo auto-escaping off

    context["PAGE"].content = page_content

    template = current_page.template
    template_content = template.content

    # Render the Template to build the complete html page:
    content = render_string_template(template_content, context)

    # insert JS/CSS data from any Plugin *after* the page rendered with the
    # django template engine:
    content = replace_add_data(context, content)

    return HttpResponse(content)




def _get_context(request, current_page_obj):
    """
    Setup the context with PyLucid objects.
    For index() and handle_command() views.
    """
    # add additional attribute
    request.anonymous_view = True

    try:
        context = RequestContext(request)
    except AttributeError, err:
        if str(err) == "'WSGIRequest' object has no attribute 'user'":
            # The auth middleware is not
            msg = (
                "The auth middleware is not activatet in your settings.py"
                " - Did you install PyLucid correctly?"
                " Please look at: %s"
                " - Original Error: %s"
            ) % (settings.INSTALL_HELP_URL, err)
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(msg)
        else:
            # other error
            raise AttributeError(err)

    context["page_msg"] = PageMessages(context)

    # Redirect every "warning" messages into the page_msg:
    redirect_warnings(context["page_msg"])

    context["PAGE"] = current_page_obj
    context["URLs"] = URLs(context)
#    context["URLs"].debug()

    # For additional JavaScript and StyleSheet information.
    # JS+CSS from internal_pages or CSS data for pygments
    # Add into the context object. Would be integraged in the page with the
    # additional_content middleware.
    context["js_data"] = []
    context["css_data"] = []

    # A list of every used html DIV CSS-ID.
    # used in PyLucid.defaulttags.lucidTag.lucidTagNode._add_unique_div()
    context["CSS_ID_list"] = []

    # add dynamic content into the context (like: login/logout link)
    add_dynamic_context(request, context)

    # Add the context to the reponse object.
    # Used in PyLucid.middlewares.additional_content
    request.CONTEXT = context

    return context


def patch_response_headers(response, cache_timeout, ETag, last_modified):
    """
    Adds some useful headers to the given HttpResponse object:
        ETag, Last-Modified, Expires and Cache-Control

    Original version: django.utils.cache.patch_response_headers()
    """
    response['ETag'] = ETag
    response['Last-Modified'] = last_modified.strftime(
        '%a, %d %b %Y %H:%M:%S GMT'
    )
    now = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(0, cache_timeout)
    response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')


def get_cached_data(url):
    """
    -Build the cache_key from the given url. Use the last page shortcut.
    -retuned the cache_key and the page data.
    """
    if url == "":
        # Request without a shortcut -> request the default page
        shortcut = "/"
    else:
        # Note: We use append_slash, but the url pattern striped the last
        #     slash out.
        # e.g.: '/page1/page2/page3' -> ['/page1/page2', 'page3'] -> 'page3'
        shortcut = url.rsplit("/",1)[-1]

    cache_key = settings.PAGE_CACHE_PREFIX + shortcut
    #print "Used cache key:", cache_key

    # Get the page data from the cache.
    response = cache.get(cache_key)

    return cache_key, response


def index(request, url):
    """
    The main index method.
    Return a normal cms page request.
    Every Request will be cached for anonymous user. For the cache_key we use
    the page shortcut from the url.
    """
    # Cache only for anonymous users. Otherwise users how are log-in don't see
    # the dynamic integrate admin menu.
    try:
        use_cache = request.user.is_anonymous()
    except AttributeError, msg:
        # TODO: middlewares not active -> _install section!
        msg = (
            "After syncdb you must activated the two django middlewares:"
            " 'SessionMiddleware' and 'AuthenticationMiddleware'"
            " Please edit your 'settings.py' file and modify the value"
            " MIDDLEWARE_CLASSES."
            " - Original Error was: %s"
        ) % msg
        raise ImproperlyConfigured(msg)

    if use_cache:
        # Try to get the cms page request from the cache
        cache_key, response = get_cached_data(url)
        if response:
            # This page has been cached in the past, use the cache data:
            return response

    setup_debug(request)

    try:
        current_page_obj = get_current_page_obj(request, url)
    except AccessDenied:
        # FIXME: We should build the command url in a better way
        #     Don't insert a hardcoded ID! Use the default ID.
        next = '?next=%s' % request.path
        path = '/'.join(
            ('',settings.COMMAND_URL_PREFIX,'1','auth','login',next)
        )
        return HttpResponseRedirect(path)
    else:
        if isinstance(current_page_obj, HttpResponse):
            # Some parts of the URL was wrong, but we found a right page
            # shortcut -> redirect to the right url
            return current_page_obj

    context = _get_context(request, current_page_obj)
    # Get the response for the requested cms page:
    response = _render_cms_page(request, context)

    if use_cache:
        # It's a anonymous user -> Cache the cms page.
        cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        # Add some headers for the browser cache
        patch_response_headers(
            response, cache_timeout,
            ETag = md5.new(cache_key).hexdigest(),
            last_modified = current_page_obj.lastupdatetime,
        )
        # Save the page into the cache
        cache.set(cache_key, response, cache_timeout)

    return response

def _get_page(request, page_id):
    """
    returns the page object.
    TODO: Check int(page_id)!
    """
    setup_debug(request)

    try:
        current_page_obj = models.Page.objects.get(id=int(page_id))
    except models.Page.DoesNotExist:
        # The ID in the url is wrong -> goto the default page
        default_page_id = get_default_page_id()
        current_page_obj = models.Page.objects.get(id=default_page_id)

        user = request.user
        if user.is_authenticated():
            # The page_msg system is not initialized, yet. So we must use the
            # low level message_set method, but this ony exist for user how are
            # login.
            # ToDo: How can we sent a message to anonymous users?
            user.message_set.create(
                message=_(
                    "Error: The page ID in the url is wrong."
                    " (goto default page.)"
                )
            )

    return current_page_obj

def handle_command(request, page_id, module_name, method_name, url_args):
    """
    handle a _command request
    """
    current_page_obj = _get_page(request, page_id)

    context = _get_context(request, current_page_obj)

    local_response = SimpleStringIO()

    if url_args == "":
        url_args = ()
    else:
        url_args = (url_args,)

    try:
        output = plugin_manager.handle_command(
            context, local_response, module_name, method_name, url_args
        )
    except AccessDenied:
        page_content = "[Permission Denied!]"
    else:
        if output == None:
            # Plugin/Module has retuned the locale StringIO response object
            page_content = local_response.getvalue()
        elif isinstance(output, basestring):
            page_content = output
        elif isinstance(output, HttpResponse):
            # e.g. send a file directly back to the client
            return output
        else:
            msg = (
                "Error: Wrong output from Plugin!"
                " - It should be write into the response object"
                " or return a String/HttpResponse object!"
                " - But %s.%s has returned: %s (%s)"
            ) % (
                module_name, method_name,
                escape(repr(output)), escape(str(type(output)))
            )
            raise AssertionError(msg)

#    print module_name, method_name
#    print page_content
#    print "---"

    if page_content:
        # Add the CSS Info, but only if the plugin has returned content and
        # not when the normal cms page rendered.
        page_content = add_css_tag(
            context, page_content, module_name, method_name
        )

    return _render_cms_page(request, context, page_content)


def redirect(request, url):
    """
    simple redirect old PyLucid URLs to the new location.
    old url:
        ".../index.py/PageShortcut/"
    new url:
        ".../PageShortcut/"
    """
    if url == "":
        url = "/"

    return HttpResponsePermanentRedirect(url)

def permalink(request, page_id):
    """
    redirect to the real page url.
    """
    current_page_obj = _get_page(request, page_id)
    url = current_page_obj.get_absolute_url()
    return redirect(request, url)
