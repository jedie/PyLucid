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

from PyLucid.models import Plugin
from PyLucid.tools.utils import escape
from PyLucid.tools.content_processors import render_string_template
from PyLucid.system.internal_page import InternalPage, InternalPageNotFound
from PyLucid.system.plugin_import import get_plugin_config, \
                                        get_plugin_version, debug_plugin_config



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

    def build_menu(self):
        """
        Build a simple menu for all plugin methods witch have a "menu_section"

        Use the internal page template "admin_menu.plugin_menu" !

        In the plugin config (plugin_manager_data) must be exist some meta
        information for the menu:
          "menu_section"     : The upper block name
          "menu_description" : Link text (optional, otherwise method name used)

        More info: http://pylucid.org/_goto/148/self-build_menu/
        """
        plugin = Plugin.objects.get(plugin_name=self.plugin_name)
        plugin_config = get_plugin_config(
            package_name = plugin.package_name,
            plugin_name = self.plugin_name,
            debug = False
        )
        plugin_version = get_plugin_version(
            package_name = plugin.package_name,
            plugin_name = self.plugin_name,
            debug = False
        )
#        debug_plugin_config(self.page_msg, plugin_config)

        plugin_manager_data = plugin_config.plugin_manager_data

        menu_data = {}
        for method_name, data in plugin_manager_data.iteritems():
            if not "menu_section" in data:
                continue

            menu_section = data["menu_section"]

            if not menu_section in menu_data:
                menu_data[menu_section] = []

            menu_data[menu_section].append(
                {
                    "link": self.URLs.methodLink(method_name),
                    "description": data.get("menu_description", method_name),
                }
            )

        self.context["PAGE"].title = "%s (%s)" % (
            self.plugin_name.replace("_", " "), plugin_version
        )

        context = {"menu_data": menu_data,}

        # Change the internal_page and use them from "admin_menu" plugin.
        plugin_internal_page = self.internal_page
        self.internal_page = InternalPage(
            self.context, plugin_name="admin_menu"
        )

        self._render_template("plugin_menu", context)#, debug=False)

        # change back to the original internal pages from the current plugin.
        self.internal_page = self.internal_page


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
            msg = "Internal page '%s' not found!" % internal_page_name
            self.page_msg.red(msg)
            return "[%s]" % msg

        self._add_js_css_data(internal_page_name)

        html = self.__render(content, context, debug)

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



