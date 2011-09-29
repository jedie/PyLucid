# coding: utf-8

"""
    Generic plugin
    ~~~~~~~~~~~~~~
    
    Simple rendering templates with some variables.

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages

from pylucid_project.apps.pylucid.decorators import render_to


@render_to()
def youtube(request, id, width=640, height=505, template_name="generic/YouTube.html", **kwargs):
    context = {
        "id": id,
        "width": width,
        "height": height,
        "template_name":template_name,
    }
    context.update(kwargs)
    return context


@render_to()
def ohloh(request, project, js_file="project_thin_badge.js", template_name="generic/ohloh.html", **kwargs):
    context = {
        "project": project,
        "js_file": js_file,
        "template_name":template_name,
    }
    context.update(kwargs)
    return context


@render_to()
def lucidTag(request, **context):
    """
    Generic plugin for inserting external widgets.
    
    Available boilerplate:
    * YouTube
    * ohloh
    
    more info:
    http://www.pylucid.org/permalink/360/generic-plugin
    
    example:
        {% lucidTag generic.youtube id="XL1UNmLDLKc" %}
        {% lucidTag generic.youtube id="XL1UNmLDLKc" width=960 height=745 %}
        {% lucidTag generic.ohloh project="pylucid" %}
        {% lucidTag generic.ohloh project="python" js_file="project_users.js?style=rainbow" %}
        {% lucidTag generic template_name="myowntemplate.html" %}
    """
    if "template_name" not in context and (request.user.is_staff or settings.DEBUG):
        messages.info(request, _("At least you must add template_name argument to {% lucidTag generic %} !"))
    else:
        return context
