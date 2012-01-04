# coding: utf-8

"""
    PyLucid unittest plugin
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    For plugin API unittest. 
    
    This plugin would be symlinked into "./pylucid_project/pylucid_plugins/" before 
    unittests starts. This would be done in pylucid_project.tests.test_tools.test_runner.
    
    note:
        You can also use the unittest_plugin in "normal" way:
            * symlink it by hand into pylucid_plugins
            * create a test PluginPage
            * request the following urls:
                .../csrf_no_decorator_view/
                .../csrf_exempt_view/
                /?unittest_plugin=csrf_test

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import http
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.log import getLogger
from django.views.decorators.csrf import csrf_exempt

from pylucid_project.apps.pylucid.models import Language
from pylucid_project.apps.pylucid.decorators import render_to


logger = getLogger("pylucid.unittest_plugin")

#_____________________________________________________________________________
# http_get_view()

GET_KEY = "unittest_plugin" # plugin name

ACTION_NONE_RESPONSE = "NoneResponse"

ACTION_STRING_RESPONSE = "StringResponse"
STRING_RESPONSE = "String response from http_get_view() unittest plugin."

ACTION_HTTP_RESPONSE = "HttpResponse"
HTTP_RESPONSE = "HttpResponse from unittest plugin."

ACTION_REDIRECT = "RedirectResponse"
REDIRECT_URL = "/"


def http_get_view(request):
    action = request.GET[GET_KEY]

    logger.debug("http_get_view() called with action: %r" % action)

    if action == "MSG_ERROR":
        logger.debug("MSG_ERROR message created.")
        messages.error(request, message="A error messages")
        return

    elif action == "csrf_test":
        return _csrf_page(request, view_name="csrf get view")

    elif action == ACTION_NONE_RESPONSE:
        # normal PageContent would be used.
        return None

    elif action == ACTION_STRING_RESPONSE:
        # replace the PageContent with the returned string.
        return STRING_RESPONSE

    elif action == ACTION_HTTP_RESPONSE:
        # replace the complete response content.
        return http.HttpResponse(content=HTTP_RESPONSE)

    elif action == ACTION_REDIRECT:
        # redirect to a url
        return http.HttpResponseRedirect(REDIRECT_URL)

    else:
        raise AssertionError("Wrong GET action parameter!")


#_____________________________________________________________________________
# CsrfTest

@render_to("unittest_plugin/csrf_info.html")
def _csrf_page(request, view_name):
    context = {
        "view_name": view_name,
        "request_dont_enforce_csrf_checks": getattr(request, "_dont_enforce_csrf_checks", None),
    }
    return context

@csrf_exempt
def csrf_exempt_view(request):
    return _csrf_page(request, view_name="csrf_exempt_view()")

def csrf_no_decorator_view(request):
    return _csrf_page(request, view_name="csrf_no_decorator_view()")


#_____________________________________________________________________________
# PluginPage views for unittests in test_pluginAPI

PLUGINPAGE_ROOT_STRING_RESPONSE = "String response from pylucid_plugins.unittest_plugin.view_root()"
PLUGINPAGE_HTTP_RESPONSE = "HttpResponse response from pylucid_plugins.unittest_plugin.test_HttpResponse()"
PLUGINPAGE_TEMPLATE_RESPONSE = "Template response from pylucid_plugins.unittest_plugin.test_plugin_template()"
PLUGINPAGE_URL_ARGS_PREFIX = "Unittest url args:"
PLUGINPAGE_URL_REVERSE_PREFIX = "Unitest url reverse:"
PLUGINPAGE_API_TEST_CONTENT = "Test content for unittest_plugin.test_PyLucid_api()"
PLUGINPAGE_API_TEST_PAGE_MSG = "page messages test for unittest_plugin.test_PyLucid_api()"

def view_root(request):
    """ String response """
    return PLUGINPAGE_ROOT_STRING_RESPONSE

def test_HttpResponse(request):
    """ replace the complete response with own HttpResponse object """
    return http.HttpResponse(PLUGINPAGE_HTTP_RESPONSE)

def test_plugin_template(request):
    """ Use own template witch use {% extends template_name %} """
    context = request.PYLUCID.context
    context["content"] = PLUGINPAGE_TEMPLATE_RESPONSE
    return render_to_response('unittest_plugin/template_test.html', context)

def test_url_args(request, arg1, arg2):
    """ test arguments in urls """
    return http.HttpResponse("%s [%r] [%r]" % (PLUGINPAGE_URL_ARGS_PREFIX, arg1, arg2))

def test_return_none(request):
    """ return None -> raised a error """
    return None

def test_url_reverse(request, url_name):
    """ Test the django url reverse function """
    url = reverse(url_name)
    return http.HttpResponse("%s [%r]" % (PLUGINPAGE_URL_REVERSE_PREFIX, url))

def test_PyLucid_api(request):
    """
    Test the PyLucid API
    see also: http://www.pylucid.org/permalink/133/pylucid-objects
    """
    messages.info(request, PLUGINPAGE_API_TEST_PAGE_MSG)

    context = request.PYLUCID.context
    output = []
    context_middlewares = request.PYLUCID.context_middlewares.keys()
    context_middlewares.sort()
    output.append("context_middlewares: %s" % context_middlewares)
    output.append("lang_entry: %r" % request.PYLUCID.current_language)
    output.append("pagetree: %r" % request.PYLUCID.pagetree)
    output.append("pagemeta: %r" % request.PYLUCID.pagemeta)

    default_lang_entry = Language.objects.get_or_create_default(request)
    output.append("default_lang_code: %s" % default_lang_entry.code)
    output.append("default_lang_entry: %r" % default_lang_entry)

    context["output"] = output
    context["content"] = PLUGINPAGE_API_TEST_CONTENT
    return render_to_response('unittest_plugin/API_test.html', context)

#_____________________________________________________________________________
# PluginPage views for unittests in test_PluginBreadcrumb

ADDED_LINK_NAME = "added-link"
ADDED_LINK_TITLE = "Unittest added link"
ADDED_LINK_URL = "the/added/url/"
ADDED_LINK_RESPONSE_STRING = "test_PluginBreadcrumb content"

def test_BreadcrumbPlugin(request):
    """
    Test view for tests.test_PluginBreadcrumb.
    Add a link to the bradcrumbs.
    """
    lang = request.PYLUCID.current_language
    breadcrumb = request.PYLUCID.request.PYLUCID.context_middlewares["breadcrumb"]
    add_url = "/%s/%s" % (lang.code, ADDED_LINK_URL)
    breadcrumb.add_link(name=ADDED_LINK_NAME, title=ADDED_LINK_TITLE, url=add_url)

    return ADDED_LINK_RESPONSE_STRING


#_____________________________________________________________________________
# Add headfiles tests

def test_add_headfiles(request):
    """
    Add content into html head with {% extrahead %} block tag in plugin template.
    """
    context = request.PYLUCID.context
    output = render_to_response('unittest_plugin/test_extrahead_blocktag.html', context)
    return output

#_____________________________________________________________________________


def test_cache(request):
    msg = request.COOKIES.get("test_messages", "not set")
    return "Response from unittest_plugin.test_cache() [%s]" % msg

def test_messages(request):
    for msg_type in ("debug", "info", "success", "warning", "error"):
        callable = getattr(messages, msg_type)
        callable(request, "A %r message" % msg_type)
    msg = request.COOKIES.get("test_messages", "not set")
    return "Response from unittest_plugin.test_messages() [%s]" % msg

