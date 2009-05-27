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
        return http.HttpResponse(content="HttpResponse from unittest plugin.")
    
    elif action==ACTION_REDIRECT:
        return http.HttpResponseRedirect(REDIRECT_URL)
    
    else:
        raise AssertionError("Wrong GET action parameter!")