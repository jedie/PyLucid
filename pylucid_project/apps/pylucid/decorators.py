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

import sys
import warnings
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.


from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect


def check_permissions(superuser_only, permissions=()):
    """
    Protect a view and limit it to users witch are log in and has the permissions.
    If the user is not log in -> Redirect him to a log in view with a next_url back to the requested page.
    
    TODO: Add a log entry, if user has not all permissions.
    
    Usage:
    --------------------------------------------------------------------------
    from pylucid_project.apps.pylucid.decorators import check_permissions
    
    @check_permissions(superuser_only=False, permissions=(u'appname.add_modelname', u'appname.change_modelname'))
    def my_view(request):
        ...
    --------------------------------------------------------------------------
    """
    assert isinstance(superuser_only, bool)
    assert isinstance(permissions, (list, tuple))

    def _inner(view_function):
        @wraps(view_function)
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
    from pylucid_project.apps.pylucid.decorators import superuser_only
    
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
    @wraps(view_function)
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_function(request, *args, **kwargs)
    return _inner


def render_to(template_name=None, debug=False):
    """
    Based on the decorators from django-annoying.

    Example:
 
        @render_to('foo/template.html')
        def PyLucidPluginFoo(request):
            bar = Bar.object.all()  
            return {'bar': bar}
        
    The view can also insert the template name in the context, e.g.:

        @render_to
        def PyLucidPluginFoo(request):
            bar = Bar.object.all()  
            return {'bar': bar, 'template_name': 'foo/template.html'}

    TODO: merge render_to() and render_pylucid_response()
    """
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            context = function(request, *args, **kwargs)

            if not isinstance(context, dict):
                if debug:
                    msg = (
                        "renter_to info: %s (template: %r)"
                        " has not return a dict, has return: %r (%r)"
                    ) % (function.__name__, template_name, type(context), function.func_code)
                    request.page_msg(msg)
                return context

            template_name2 = context.pop('template_name', template_name)
            assert template_name2 != None, \
                ("Template name must be passed as render_to parameter"
                " or 'template_name' must be inserted into context!")

            response = render_to_response(template_name2, context, context_instance=RequestContext(request))

            if debug:
                request.page_msg("render debug for %r (template: %r):" % (function.__name__, template_name2))
                request.page_msg("local view context:", context)
                request.page_msg("response:", response.content)

            return response
        return wrapper
    return renderer
