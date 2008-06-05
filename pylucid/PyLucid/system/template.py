# -*- coding: utf-8 -*-

"""
    template tools
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import traceback

from django.shortcuts import render_to_response

from PyLucid.install.BaseInstall import get_base_context
from PyLucid.models import Page, Template


def get_template_obj(response, current_page):
    assert isinstance(current_page, Page)
    template_id = current_page.template
    return Template.objects.get(id__exact=template_id)

def get_template_content(response, current_page):
    assert isinstance(current_page, Page)
    template = get_template_obj(response, current_page)
    return template.content


def render_help_page(request, error_msg, e):
    """
    Send the help page "install_info.html" to the user.
    """
    context = get_base_context(request)
    context["error_msg"] = error_msg
    context["exception"] = repr(e)
    if getattr(request, "debug", False):
        context["traceback"] = traceback.format_exc()
    return render_to_response("install_info.html", context)