# coding: utf-8

"""
    PyLucid unittest plugin
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    For plugin API unittest. 
    
    This plugin would be symlinked into "./pylucid_project/pylucid_plugins/" before 
    unittests starts. This would be done in pylucid_project.tests.test_tools.test_runner.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import http

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
    
    if action==ACTION_NONE_RESPONSE:
        # normal PageContent would be used.
        return None
    
    elif action==ACTION_STRING_RESPONSE:
        # replace the PageContent with the returned string.
        return STRING_RESPONSE
    
    elif action==ACTION_HTTP_RESPONSE:
        # replace the complete response content.
        return http.HttpResponse(content=HTTP_RESPONSE)
    
    elif action==ACTION_REDIRECT:
        # redirect to a url
        return http.HttpResponseRedirect(REDIRECT_URL)
    
    else:
        raise AssertionError("Wrong GET action parameter!")


#_____________________________________________________________________________
# PluginPage views

PLUGINPAGE_ROOT_STRING_RESPONSE = "String response from unittest_plugin.view_root()"
PLUGINPAGE_VIEW_A_STRING_RESPONSE = "HttpResponse response from unittest_plugin.view_a()"

def view_root(request):
    """ String response """
    return PLUGINPAGE_ROOT_STRING_RESPONSE

def view_a(request):
    """ replace the complete response with own HttpResponse object """
    return http.HttpResponse(PLUGINPAGE_VIEW_A_STRING_RESPONSE)

def view_b(request, url):
    """ Test """
    url2 = reverse("PluginTest-view_c")
    return HttpResponse("response: %r pluginpage_text.view_b: %r" % (url2, url))

def view_c(request):
    return HttpResponse("response: pluginpage_text.view_c !")