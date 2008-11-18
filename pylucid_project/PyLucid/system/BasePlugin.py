# -*- coding: utf-8 -*-

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

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
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

        self.request    = context["request"]
        self.response   = response
        self.context    = context

        self.page_msg   = self.request.page_msg
        self.URLs       = context["URLs"]
        self.URLs.current_plugin = self.plugin_name

        self.current_page = self.context["PAGE"]

    def get_preferences(self, id=None):
        """
        returns the preferences from the database as a dict
        """
        preference = Plugin.objects.get_preferences(self.plugin_name, id)
        return preference

    def set_preferences(self, key, value, id=None):
        """
        set a new value to one preferences entry
        """
        user = self.request.user
        data_dict = Plugin.objects.set_preferences(
            self.plugin_name, key, value, user, id
        )
        return data_dict

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
        )
        plugin_version = get_plugin_version(
            package_name = plugin.package_name,
            plugin_name = self.plugin_name,
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
        self.internal_page = plugin_internal_page


    def _add_js_css_data(self, internal_page_name):
        """
        insert the additional JavaScript and StyleSheet data into the global
        context.
        page_style.replace_add_data() puts the file links into the page.
        """
        def is_added(slug_list, url):
            for entry in slug_list:
                if entry["url"] == url:
                    return True
            return False
            
        for slug in ("js", "css"):
            url = self.internal_page.get_url(internal_page_name, slug)
            if url == None:
                continue
            
            slug_list = self.context["%s_data" % slug]
            if is_added(slug_list, url):
                # The same url has been added in the past -> skip
                continue
                        
            slug_list.append({
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

    def __render(self, template, context, debug=False):
        """
        render the template string with the given context and returned it.
        -debug the context, if debug is on.
        """
        html = render_string_template(template, context)

        if debug:
            self.response.write("<fieldset><legend>template debug:</legend>")

            self.response.write("<legend>context:</legend>")
            self.response.write("<pre>")
            self.response.write(escape(pprint.pformat(context)))
            self.response.write("</pre>")

            self.response.write("<legend>template:</legend>")
            self.response.write("<pre>")
            self.response.write(escape(template))
            self.response.write("</pre>")

            if debug>1:
                self.response.write("<legend>result html code:</legend>")
                self.response.write("<pre>")
                self.response.write(escape(html))
                self.response.write("</pre>")

            self.response.write("</fieldset>")

        return html

    def error(self, public_msg, debug_msg):
        """
        Display a error with page_msg.red().
        Append debug_msg if self.request.debug is on
        e.g.:
            try:
                ...do something...
            except Exception, err:
                return self.error(_("Wrong URL."), err)
        """
        msg = public_msg
        if self.request.debug:
            msg += " %s" % debug_msg

        self.page_msg.red(msg)


