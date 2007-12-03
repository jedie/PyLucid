#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid stylesheets
    ~~~~~~~~~~~~~~~~~~~

    - Put the css html tag into the cms page.
    - Send the current stylesheet directly to the client.

    Note:
    1. The page_style plugin insert the temporary ADD_DATA_TAG *before* the
        global Stylesheet inserted. So the global Stylesheet can override CSS
        properties from every internal page.
        The ADD_DATA_TAG would be replaced with the collected CSS/JS contents
        in PyLucid.index *after* the page rendered with the django template
        engine.
    2. In CGI environment you should use print_current_style() instead of
        lucidTag! Because the lucidTag insert only the link to the stylesheet.
        Every page request causes a stylesheet request, in addition!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


__version__= "$Rev$"


import sys, os, datetime

from django.http import HttpResponse
from django.conf import settings

from PyLucid.models import Style
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.content_processors import render_string_template
from PyLucid.db.internal_pages import get_internal_page

class page_style(PyLucidBasePlugin):

    def lucidTag(self):
        """
        -Put a link to sendStyle into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet link
        """
        self.response.write(settings.ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        style_name = current_page.style.name
        style_filename = "%s.css" % style_name

        url = self.URLs.methodLink("sendStyle")
        url = url + style_filename

        cssTag = '<link rel="stylesheet" type="text/css" href="%s" />\n' % url
        self.response.write(cssTag)


    def print_current_style(self):
        """
        -Write the stylesheet directly into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet content.

        Used with the tag: {% lucidTag page_style.print_current_style %}
        """
        self.response.write(settings.ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        stylesheet = current_page.style

        context = {
            "content": stylesheet.content,
        }
        self._render_template("write_styles", context)#, debug=True)


    def sendStyle(self, css_filename):
        """
        send the stylesheet as a file to the client.
        It's the request started with the link tag from self.lucidTag() ;)
        TODO: Should insert some Headers for the browser cache.
        """
        css_name = css_filename.split(".",1)[0]

        try:
            style = Style.objects.get(name=css_name)
        except Style.DoesNotExist:
            raise Http404("Stylesheet '%s' unknown!" % cgi.escape(css_filename))

        content = style.content

        response = HttpResponse()
        response['Content-Type'] = 'text/css; charset=utf-8'
        response.write(content)

        return response


def replace_add_data(context, content):
    """
    Replace the temporary inserted "add data" tag, with all collected CSS/JS
    contents, e.g. from the internal pages.
    Note: The tag added in PyLucid.plugins_internal.page_style
    """

    internal_page = get_internal_page("page_style", "add_data")
    internal_page_content = internal_page.content_html

    context = {
        "js_data": context["js_data"],
        "css_data": context["css_data"],
    }
    html = render_string_template(
        internal_page_content, context, autoescape=False
    )

    content = content.replace(settings.ADD_DATA_TAG, html)
    return content