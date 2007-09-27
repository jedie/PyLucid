#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    {% lucidTag ... %}
    ~~~~~~~~~~~~~~~~~~

    the special PyLucid tag who starts a plugin with the plugin manager.
    e.g.: {% lucidTag plugin_name.method_name key1="value1" key2="value2" %}

    registered in: ./PyLucid/defaulttags/__init__.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import cgi, re

from PyLucid.system.plugin_manager import run
from PyLucid.system.response import SimpleStringIO
from PyLucid.tools.shortcuts import makeUnique

from django.conf import settings
from django import template


# FIXME: The re should be more fault-tolerant:
KWARGS_REGEX = re.compile('''(\w*?)\=['"](.*?)['"]''')


class lucidTagNodeError(template.Node):
    """
    display a error messages in the cms page for a wrong lucidTag.
    """
    def __init__(self, plugin_name, method_name, msg):
        self.plugin_name = plugin_name
        self.method_name = method_name
        self.msg = msg

    def render(self, context):
        txt = "[lucidTag %s.%s syntax error: %s]" % (
            self.plugin_name, self.method_name, self.msg
        )
        return txt


class lucidTagNode(template.Node):
    def __init__(self, plugin_name, method_name, method_kwargs):
        self.plugin_name = plugin_name
        self.method_name = method_name
        self.method_kwargs = method_kwargs

    def __repr__(self):
        return "<lucidTag node ('%s.%s' kwargs:%s)>" % (
            self.plugin_name, self.method_name, self.method_kwargs
        )

    def _add_unique_div(self, context, content):
        """
        Add a html DIV tag with a unique CSS-ID and a class name defined in
        the settings.py
        """
        id = self.plugin_name + "_" + self.method_name
        id = makeUnique(id, context["CSS_ID_list"])
        context["CSS_ID_list"].append(id)

        return u'<div class="%s %s" id="%s">\n%s\n</div>\n' % (
            settings.CSS_DIV_CLASS_NAME, self.plugin_name, id, content
        )

    def render(self, context):
        local_response = SimpleStringIO()
        output = run(
            context, local_response,
            self.plugin_name, self.method_name,
            method_kwargs = self.method_kwargs
        )
        if output == None:
            content = local_response.getvalue()
        elif isinstance(output, basestring):
            content = output
        else:
            msg = (
                "Error: Wrong output from inline Plugin!"
                " - It should be write into the response object and return None"
                " or return a basestring!"
                " - But %s.%s has returned: %s (%s)"
            ) % (
                self.plugin_name, self.method_name,
                repr(output), type(output)
            )
            raise AssertionError(msg)

        content = self._add_unique_div(context, content)

        return content


def lucidTag(parser, token):
    """
    Parse the lucidTags.

    syntax e.g.:
        {% lucidTag PluginName %}
        {% lucidTag PluginName kwarg1="value1" %}
        {% lucidTag PluginName kwarg1="value1" kwarg2="value2" %}
    """
    content = token.contents
    content = content.split(" ", 2)[1:]
    plugin_name = content.pop(0)

    method_kwargs = {}
    if content:
        kwargs = content[0]
        kwargs = KWARGS_REGEX.findall(kwargs)
        for key, value in kwargs:
            # method Keywords must be Strings
            key = key.encode(settings.DEFAULT_CHARSET)
            method_kwargs[key] = value

    if "." in plugin_name:
        plugin_name, method_name = plugin_name.split(".", 1)
    else:
        method_name = "lucidTag"

    return lucidTagNode(plugin_name, method_name, method_kwargs)

