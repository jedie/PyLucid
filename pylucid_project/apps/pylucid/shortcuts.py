# coding:utf-8

"""
    PyLucid shortcuts
    ~~~~~~~~~~~~~~~~~
    
    render_pylucid_response() - Similar to django.shortcuts.render_to_response, can be used in
        PyLucid plugin "ajax+normal response" views.

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.models.log import LogEntry


def ajax_response(request, template_name, context, **kwargs):
    response_content = render_to_string(template_name, context, **kwargs)

    # Get the extrahead storage (pylucid.system.extrahead.ExtraHead)
    extrahead = request.PYLUCID.extrahead

    # Get the extra head content as a string
    extra_head_content = extrahead.get()

    # insert the extra head content into the response content
    # Note: In a ajax view the {% extrahead %} block would normaly not rendered into
    # the response content. Because the view returns a HttpResponse object, so all
    # other processing skip and all PyLucid context middleware (in the global template)
    # would not rendered.
    response_content = mark_safe(extra_head_content + "\n" + response_content)

    http_response_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(response_content, **http_response_kwargs)


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
    if request.is_ajax():
#        print "make ajax response..."
        return ajax_response(request, template_name, context, **kwargs)

    response_content = render_to_string(template_name, context, **kwargs)
#    print "make normal response..."
    # Non-Ajax request: the string content would be replace the page content.
    # The {% extrahead %} content would be inserted into the globale template with
    # the PyLucid context middleware pylucid_plugin.extrahead.context_middleware
#    response = HttpResponse(response_content)
#    response.replace_main_content = True # Plugin replace the page content
#    return response
    return response_content


def bad_request(app_label, action, debug_msg):
    """
    Create a new LogEntry and return a HttpResponseBadRequest
    """
    LogEntry.objects.log_action(
        app_label=app_label, action=action, message=debug_msg,
    )
    if settings.DEBUG:
        msg = debug_msg
    else:
        msg = ""

    return HttpResponseBadRequest(msg)

