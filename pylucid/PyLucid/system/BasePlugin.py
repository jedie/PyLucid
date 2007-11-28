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


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import pprint

from django.utils.safestring import mark_safe

from PyLucid.db.internal_pages import get_internal_page
from PyLucid.tools.content_processors import apply_markup, \
                                                        render_string_template
from PyLucid.tools.content_processors import escape

class PyLucidBasePlugin(object):

    def __init__(self, context, response):
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


    def _get_template(self, internal_page_name):
        """
        retuned the internal page object
        Get the plugin name throu the superior class name
        """
        plugin_name = self.__class__.__name__
        internal_page = get_internal_page(plugin_name, internal_page_name)
        return internal_page

    def _add_js_css_data(self, internal_page):
        """
        insert the additional JavaScript and StyleSheet data into the global
        context.
        """
        def add(attr_name, key):
            content = getattr(internal_page, attr_name)
            if content == "":
                # Nothig to append ;)
                return

            self.context[key].append({
                "from_info": "internal page: '%s'" % internal_page.name,
                "data": content,
            })

        # append the JavaScript data
        add("content_js", "js_data")

        # append the StyleSheet data
        add("content_css", "css_data")


    def _get_rendered_template(self, internal_page_name, context, debug=False):
        """
        return a rendered internal page
        """
        internal_page = self._get_template(internal_page_name)

        content_html = internal_page.content_html

        self._add_js_css_data(internal_page)

        html = self.__render(content_html, context, debug)

        markup_object = internal_page.markup
        html = apply_markup(html, self.context, markup_object)

        return html

    def _render_template(self, internal_page_name, context, debug=False):
        """
        render a template and write it into the response object
        """
        html = self._get_rendered_template(internal_page_name, context, debug)
        html = mark_safe(html) # turn djngo auto-escaping off
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



