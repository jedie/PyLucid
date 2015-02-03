# coding: utf-8

"""
    PyLucid context middlewares
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    For PyLucid context middlewares API.
    see:
        http://www.pylucid.org/permalink/134/new-v09-plugin-api#context-middleware
    
    :copyleft: 2012-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from django.contrib import messages


TAG_RE = re.compile("<!-- ContextMiddleware (.*?) -->", re.UNICODE)


class PyLucidContextMiddlewares(object):
    _MIDDLEWARES = {}

    def __init__(self):
        """
        Collect all context_middleware class objects from all existing pylucid plugins
        """
        for plugin_name, plugin_instance in PYLUCID_PLUGINS.items():
            try:
                middleware_class = plugin_instance.get_plugin_object("context_middleware", "ContextMiddleware")
            except plugin_instance.ObjectNotFound, err:
                pass
            else:
                self._MIDDLEWARES[plugin_name] = middleware_class
#        print "***", self._MIDDLEWARES

    def process_request(self, request):
        """ initialize all existing context middleware classes """
        request.PYLUCID.context_middlewares = {}

        for plugin_name, middleware_class in self._MIDDLEWARES.items():
            # make ContextMiddleware instance
            instance = middleware_class(request)
            # Make instance accessible via request object 
            request.PYLUCID.context_middlewares[plugin_name] = instance
            #messages.debug(request, "Init ContextMiddleware %r" % plugin_name)

    def process_response(self, request, response):
        """
        replace the context middleware tags in the response, with the plugin render output
        """
        if (response.status_code != 200
            or not isinstance(response, HttpResponse)
            or "html" not in response["content-type"]):
            # No HTML Page -> do nothing
            return response

        # FIXME: A HttpResponse allways convert unicode into string. So we need to do that here:
        # Or we say, context render should not return a HttpResponse?
    #    from django.utils.encoding import smart_str
    #    complete_page = smart_str(complete_page)

        source_content = response.content

        self.request = request # used in sub function
        new_content = TAG_RE.sub(self._replace, source_content)
        response.content = new_content
        return response

    def _replace(self, match):
        """
        function for TAG_RE.sub: Replace the context middleware tags
        """
        request = self.request

        context_middlewares = request.PYLUCID.context_middlewares
        plugin_name = match.group(1)
        try:
            middleware_class_instance = context_middlewares[plugin_name]
        except KeyError, err:
            return "[Error: context middleware %r doesn't exist! Existing middlewares are: %r]" % (
                plugin_name, context_middlewares.keys()
            )

        # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
        request.plugin_name = plugin_name
        request.method_name = "ContextMiddleware"

        middleware_response = middleware_class_instance.render()

        request.plugin_name = None
        request.method_name = None

        if middleware_response == None:
            return ""
        elif isinstance(middleware_response, unicode):
            return smart_str(middleware_response, encoding=settings.DEFAULT_CHARSET)
        elif isinstance(middleware_response, str):
            return middleware_response
        elif isinstance(middleware_response, HttpResponse):
            return middleware_response.content
        else:
            raise RuntimeError(
                "plugin context middleware render() must return"
                " http.HttpResponse instance or a basestring or None!"
            )
