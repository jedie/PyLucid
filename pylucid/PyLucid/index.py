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

from django.http import HttpResponse, HttpResponsePermanentRedirect, \
                                                           HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from PyLucid.models import Page
from PyLucid.system import plugin_manager
from PyLucid.system.URLs import URLs
from PyLucid.system.page_msg import PageMessages
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.exceptions import AccessDenied
from PyLucid.system.context_processors import add_dynamic_context, add_css_tag
from PyLucid.system.detect_page import get_current_page_obj, \
                                                            get_default_page
from PyLucid.tools.utils import escape, escape_django_tags
from PyLucid.tools.content_processors import apply_markup, \
                                    render_string_template, redirect_warnings
from PyLucid.plugins_internal.page_style.page_style import replace_add_data


def _render_cms_page(request, context, page_content=None):
    """
    render the cms page.
    - render a normal cms request
    - render a _command request: The page.content is the output from the plugin.
    """
    if request.anonymous_view == False:
        # TODO: remove in v0.9, see: ticket:161
        # context["robots"] was set in contex_processors.static()
        # Hide the response from search engines
        context["robots"] = "NONE,NOARCHIVE"

    context["anonymous_view"] = request.anonymous_view

    current_page = context["PAGE"]

    if page_content:
        # The page content comes e.g. from the _command plugin
#        current_page.content = page_content
        page_content = escape_django_tags(page_content)
    else:
        # get the current page data from the db
        page_content = current_page.content

        markup_no = current_page.markup
        page_content = apply_markup(page_content, context, markup_no)

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

    context = RequestContext(request)

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


def index(request, url):
    """
    The main index method.
    Return a normal cms page request.
    Every Request will be cached for anonymous user. For the cache_key we use
    the page shortcut from the url.
    """
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

    if getattr(request, "_use_cache", None) == None:
        # Set _use_cache information for the PyLucid cache middleware, but only
        # if it was set to true or false in the past
        request._use_cache = True

    return response


def _get_page(request, page_id):
    """
    returns the page object.
    TODO: Check int(page_id)!
    """
    try:
        current_page_obj = Page.objects.get(id=int(page_id))
    except Page.DoesNotExist:
        # The ID in the url is wrong -> goto the default page
        current_page_obj = get_default_page(request)

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
        if request.debug:
            # don't use errorhandling -> raise the prior error
            raise
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
