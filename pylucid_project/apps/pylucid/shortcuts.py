# coding:utf-8

"""
    PyLucid shortcuts
    ~~~~~~~~~~~~~~~~~
    
    render_pylucid_response() - Similar to django.shortcuts.render_to_response, can be used in
        PyLucid plugin "ajax+normal response" views.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import warnings

from django import http
from django.template.loader import render_to_string

from django_tools.middlewares import ThreadLocal


def render_pylucid_response(request, template_name, context, **kwargs):
    """
    Similar to django.shortcuts.render_to_response.
    
    If it's a ajax request: insert extra head content and return a HttpResponse object.
    This will be send directly back to the client.
    
    If it's not a ajax request: render the plugin template and return it as a String: So it
    will be replace the cms page content in the global template. The complete page would be
    rendered.
    
    TODO: merge render_to() and render_pylucid_response()
    """
    response_content = render_to_string(template_name, context, **kwargs)

    if request.is_ajax():
        #if settings.DEBUG: print "make ajax response..."

        # Get the extrahead storage (pylucid.system.extrahead.ExtraHead)
        extrahead = request.PYLUCID.extrahead

        # Get the extra head content as a string
        extra_head_content = extrahead.get()

        # insert the extra head content into the response content
        # Note: In a ajax view the {% extrahead %} block would normaly not rendered into
        # the response content. Because the view returns a HttpResponse object, so all
        # other processing skip and all PyLucid context middleware (in the global template)
        # would not rendered.
        response_content = extra_head_content + "\n" + response_content

        http_response_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
        return http.HttpResponse(response_content, **http_response_kwargs)
    else:
        # Non-Ajax request: the string content would be replace the page content.
        # The {% extrahead %} content would be inserted into the globale template with
        # the PyLucid context middleware pylucid_plugin.extrahead.context_middleware
        return response_content



def failsafe_message(msg):
    """
    Display a message to the user. Try to use:
    1. PyLucid page_msg
    2. django user messages
    3. Python warnings
    """
    # Try to create a PyLucid page_msg
    request = ThreadLocal.get_current_request()
    if request and hasattr(request, "page_msg"):
        request.page_msg(msg)
        return

    # Try to use django user message systen.
    user = ThreadLocal.get_current_user()
    if user:
        # import User here, otherwise failsafe_message() is
        # not usable before environment is full initialized.
        from django.contrib.auth.models import User
        if isinstance(user, User):
            user.message_set.create(message=msg)
            return

    # use normal warnings
    warnings.warn(msg)
