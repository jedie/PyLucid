# -*- coding: utf-8 -*-

"""
    PyLucid common middleware
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Big work-a-round for the install section. Some django middlewares needs
    his database tables. The user can create it with syncdb in the _install
    section. So we need a way to activate the middlewares only if syncdb was
    done in the past.
    Here we try to load all middlewares. If a "no such table" error occurs
    we send a info page to the user.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings

#try:
#    from threading import local
#except ImportError:
#    from django.utils._threading_local import local

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.middleware.locale import LocaleMiddleware

from PyLucid.system.exceptions import LowLevelError
from PyLucid.system.template import render_help_page
from PyLucid.system.utils import setup_request


session_middleware = SessionMiddleware()
auth_middleware = AuthenticationMiddleware()
locale_middleware = LocaleMiddleware()

#_thread_locals = local()
#
#def get_local_request():
#    """
#    Get current threading local request object
#    """
#    return _thread_locals.request
##    return getattr(_thread_locals, 'request', None)


def raise_non_table_error(e):
    """
    Raise the original error, if it is not the table access problem.
    """
    err_msg = str(e)
    if not "no such table" in err_msg:
        # raise the previouse error
        raise

    if "PyLucidPlugins_" in err_msg:
        # raise the previouse error for missing plugin models tables
        raise


class PyLucidCommonMiddleware(object):
    """
    Load the django middlewares:
        - 'django.contrib.sessions.middleware.SessionMiddleware'
        - 'django.contrib.auth.middleware.AuthenticationMiddleware'
        - 'django.middleware.locale.LocaleMiddleware'

    If the database tables not created (syncdb not executed, yet) send the user
    a help page.
    """
    def process_request(self, request):
        # add "debug" and "page_msg" to the request object. Redirect warnings.
        setup_request(request)

        # Attach the current request
#        _thread_locals.request = request

        try:
            session_middleware.process_request(request)
            auth_middleware.process_request(request)
            locale_middleware.process_request(request)
        except Exception, e:
            raise_non_table_error(e)
            # These exist no database tables, the django session/auth middelware
            # can't work. But e.g. in the PyLucid cache middleware we check if
            # the user is anonymous, so we add the anonymous user object here:
            # django.contrib.auth.models.AnonymousUser
            request.user = AnonymousUser()

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            # start the view
            return view_func(request, *view_args, **view_kwargs)
        except LowLevelError, e:
            error_msg, e = e
            return render_help_page(request, error_msg, e)
        except Exception, e:
            raise_non_table_error(e)

            url = request.META["PATH_INFO"]
            if settings.INSTALL_URL_PREFIX in url or \
                                                settings.MEDIA_URL in url:
                # Skip the middleware, if we are in the _install section or
                # it's a static file request with the dev. server
                return

            error_msg = "Can't get a database table."
            return render_help_page(request, error_msg, e)


    def process_response(self, request, response):
        try:
            return session_middleware.process_response(request, response)
        except Exception, e:
            raise_non_table_error(e)

        return response

