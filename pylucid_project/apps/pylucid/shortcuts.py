# coding:utf-8

"""
    PyLucid shortcuts
    ~~~~~~~~~~~~~~~~~
    
    render_pylucid_response() - Similar to django.shortcuts.render_to_response, can be used in
        PyLucid plugin "ajax+normal response" views.

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import http
from django.template.loader import render_to_string


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




