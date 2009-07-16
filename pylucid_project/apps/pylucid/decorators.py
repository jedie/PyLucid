# coding: utf-8

"""
    PyLucid decorators
    ~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import warnings

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission


def check_permissions(superuser_only, permissions=()):
    """
    Protect a view and limit it to users witch are log in and has the permissions.
    If the user is not log in -> Redirect him to a log in view with a next_url back to the requested page.
    
    TODO: Add a log entry, if user has not all permissions.
    
    Usage:
    --------------------------------------------------------------------------
    from pylucid.decorators import check_permissions
    
    @check_permissions([u'appname.add_modelname', u'appname.change_modelname'])
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    """
    assert isinstance(superuser_only, bool)
    assert isinstance(permissions, (list, tuple))

    def _inner(view_function):
        def _check_permissions(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated():
                request.page_msg.error("Permission denied for anonymous user. Please log in.")
                url = settings.PYLUCID.AUTH_NEXT_URL % {"path": "/", "next_url": request.path}
                return HttpResponseRedirect(url)

            if not user.has_perms(permissions):
                msg = "User %r has not all permissions: %r (existing permissions: %r)" % (
                    user, permissions, user.get_all_permissions()
                )
                if settings.DEBUG: # Usefull??
                    warnings.warn(msg)
                raise PermissionDenied(msg)
            return view_function(request, *args, **kwargs)

        # Add superuser_only and permissions attributes, so they are accessible
        # Used to build the admin menu
        _check_permissions.superuser_only = superuser_only
        _check_permissions.permissions = permissions

        return _check_permissions
    return _inner


def superuser_only(view_function):
    """
    Limit view to superusers only.
    TODO: Add a log entry, if PermissionDenied raised.
    
    Usage:
    --------------------------------------------------------------------------
    from pylucid.decorators import superuser_only
    
    @superuser_only
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    
    or in urls:
    
    --------------------------------------------------------------------------
    urlpatterns = patterns('',
        (r'^foobar/(.*)', is_staff(my_view)),
    )
    --------------------------------------------------------------------------    
    """
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_function(request, *args, **kwargs)
    return _inner
