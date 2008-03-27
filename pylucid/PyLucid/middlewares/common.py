#!/usr/bin/env python
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

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.conf import settings

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.middleware.locale import LocaleMiddleware

from PyLucid.system.exceptions import LowLevelError
from PyLucid.system.template import render_help_page
from PyLucid.system.utils import setup_debug


session_middleware = SessionMiddleware()
auth_middleware = AuthenticationMiddleware()
locale_middleware = LocaleMiddleware()


def raise_non_table_error(e):
    """
    Raise the original error, if it is not the table access problem.
    """
    if not "no such table" in str(e):
        # raise the previouse error
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
        # add the attribute "debug" to the request object.
        setup_debug(request)

        try:
            session_middleware.process_request(request)
            auth_middleware.process_request(request)
            locale_middleware.process_request(request)
        except Exception, e:
            raise_non_table_error(e)

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

