# -*- coding: utf-8 -*-

"""
    PyLucid page cache debug
    ~~~~~~~~~~~~~~~~~~~~~~~~

    A hackish debugger for django CacheMiddleware.

    Append the cache update variable request._cache_update_cache into every
    response.

    Should be only used for dev debugging and not for production ;)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

class DebugPageCache(object):
    """
    Debug django CacheMiddleware
    """
    def __init__(self):
        self.func_name = None
        self.__cache_update_cache = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Save the view function name.
        """
        self.func_name = view_func.func_name

    def process_response(self, request, response):
        """
        Append the repr() of request._cache_update_cache
        """
        if self.func_name == None:
            # Not a normal response (e.g. Redirect) -> do nothing.
            return response

        if hasattr(request, '_cache_update_cache'):
            self.__cache_update_cache = request._cache_update_cache

        info = "request._cache_update_cache: '%s' ('%s' view) " % (
            repr(self.__cache_update_cache), self.func_name
        )

        content = response.content
        if "html" in response._headers["content-type"][1]:
            # Try to insert the info into a html valid way.
            old_content = content
            content = content.replace("</body>", "<h1>%s</h1></body>" % info)
            if content == old_content:
                # replacement not successful -> append it.
                content += "\n\n" + info
        else:
            # Not a html reponse -> Append the info
            content += "\n\n" + info

        response.content = content

        return response

