#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid BasePlugin
    ~~~~~~~~~~~~~~~~~~

    The base Plugin object. Every Plugin can inherit.

    e.g.:

        from PyLucid.system.BasePlugin import PyLucidBasePlugin

        class Bsp(PyLucidBasePlugin):
            def __init__(self, *args, **kwargs):
                super(Bsp, self).__init__(*args, **kwargs)

    Know issues:
        The page cache doesn't update, if the content changed.
        So, PyLucid must reloaded (dev. server + fastCGI).
        Never mind, becuase in future version, we don't save the internal
        pages into the database ;)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, pprint

from django.conf import settings
from django.utils.safestring import mark_safe

from PyLucid.tools.content_processors import apply_markup, \
                                                        render_string_template
from PyLucid.tools.utils import escape
from PyLucid.system.internal_page import InternalPage, InternalPageNotFound


class PyLucidBasePlugin(object):

    def __init__(self, context, response):
        self.plugin_name = self.__class__.__name__
        self.internal_page = InternalPage(context, self.plugin_name)

        self.context    = context
        self.response   = response

        self.request    = context["request"]
        self.page_msg   = context["page_msg"]
        self.URLs       = context["URLs"]

        self.current_page = self.context["PAGE"]

    def _debug_context(self, context, template):
        self.response.write("<fieldset><legend>template debug:</legend>")
        self.response.write("<legend>context:</legend>")
        self.response.write("<pre>")
        pprint_context = pprint.pformat(context)
        self.response.write(escape(pprint_context))
        self.response.write("</pre>")
        self.response.write("<legend>template:</legend>")
        self.response.write("<pre>")
        template = escape(template)
        # Escape all django template tags
        template = template.replace("{", "&#x7B;").replace("}", "&#x7D;")
        self.response.write(template)
        self.response.write("</pre></fieldset>")


    def _add_js_css_data(self, internal_page_name):
        """
        insert the additional JavaScript and StyleSheet data into the global
        context.
        page_style.replace_add_data() puts the file links into the page.
        """
        for slug in ("js", "css"):
            url = self.internal_page.get_url(internal_page_name, slug)
            if url == None:
                continue
            self.context["%s_data" % slug].append({
                "plugin_name": self.plugin_name,
                "url": url,
            })

    def _get_rendered_template(self, internal_page_name, context, debug=False):
        """
        return a rendered internal page
        """
        try:
            content = self.internal_page.get_content(internal_page_name, "html")
        except InternalPageNotFound:
            self.page_msg.red(
                "Internal page '%s' not found!" % internal_page_name
            )
            return

        self._add_js_css_data(internal_page_name)

        html = self.__render(content, context, debug)

        # FIXME: Should be remove the markup function in internal pages?
#        markup_object = internal_page.markup
#        html = apply_markup(html, self.context, markup_object)

        html = mark_safe(html) # turn djngo auto-escaping off
        return html

    def _render_template(self, internal_page_name, context, debug=False):
        """
        render a template and write it into the response object
        """
        html = self._get_rendered_template(internal_page_name, context, debug)
        self.response.write(html)

    def _render_string_template(self, template, context, debug=False):
        """
        Render a string-template with the given context.
        Should be only used for developing. The normal way is: Use a internal
        page for templates.
        """
        html = self.__render(template, context, debug)
        self.response.write(html)

    def __render(self, content, context, debug=False):
        """
        render the content string with the given context and returned it.
        -debug the context, if debug is on.
        """
        if debug:
            self._debug_context(context, content)

        html = render_string_template(content, context)
        return html



