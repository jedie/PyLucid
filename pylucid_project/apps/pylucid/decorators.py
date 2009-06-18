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
from django.core.exceptions import PermissionDenied



def check_permissions(permissions):
    """
    TODO: Add a log entry, if user has not all permissions.
    
    Usage:
    --------------------------------------------------------------------------
    from pylucid.decorators import check_permissions
    
    @check_permissions([u'appname.add_modelname', u'appname.change_modelname'])
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    """
    assert isinstance(permissions, (list, tuple))
    
    def _inner(view_function):
        def _check_permissions(request, *args, **kwargs):    
            user = request.user
            
            if not user.is_authenticated():
                msg = "Permission denied for anonymous user."
                if settings.DEBUG: # Usefull??
                    warnings.warn(msg)
                raise PermissionDenied(msg)
                
            if not user.has_perms(permissions):
                msg = "User %r has not all permissions: %r (existing permissions: %r)" % (
                    user, permissions, user.get_all_permissions()
                )
                if settings.DEBUG: # Usefull??
                    warnings.warn(msg)
                raise PermissionDenied(msg)
            return view_function(request, *args, **kwargs)
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