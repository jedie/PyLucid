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

import cgi

from PyLucid.system.plugin_manager import run
from PyLucid.system.response import SimpleStringIO
from PyLucid.tools.shortcuts import makeUnique

from django.conf import settings
from django import template


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

        try:
            return u'<div class="%s" id="%s">\n%s\n</div>\n' % (
                settings.CSS_DIV_CLASS_NAME, id, content
            )
        except UnicodeDecodeError:
            # FIXME: In some case (with mysql_old) we have trouble here.
            # I get this traceback on www.jensdiemer.de like this:
            #
            #Traceback (most recent call last):
            #File ".../django/template/__init__.py" in render_node
            #    750. result = node.render(context)
            #File ".../PyLucid/defaulttags/lucidTag.py" in render
            #    102. content = self._add_unique_div(context, content)
            #File ".../PyLucid/defaulttags/lucidTag.py" in _add_unique_div
            #    73. return u'<div class="%s" id="%s">\n%s\n</div>\n' % (
            #
            #UnicodeDecodeError at /FH-D-sseldorf/
            #'ascii' codec can't decode byte 0xc3 in position 55: ordinal not in range(128)
            #
            #content += "UnicodeDecodeError hack active!"
            return '<div class="%s" id="%s">\n%s\n</div>\n' % (
                str(settings.CSS_DIV_CLASS_NAME), str(id), content
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
    # split content:
    # e.g.: {% lucidTag PluginName kwarg1="value1" kwarg2="value2" %}
    # plugin_name = "PluginName"
    # kwargs = ['par1="value1"', 'par2="value2"']
    kwargs = token.contents.split()[1:]
    plugin_name = kwargs.pop(0)

    if "." in plugin_name:
        plugin_name, method_name = plugin_name.split(".", 1)
    else:
        method_name = "lucidTag"

    # convert the kwargs list into a dict
    # in..: ['par1="value1"', 'par2="value2"']
    # out.: {'par1': 'value1', 'par2': 'value2'}
    method_kwargs = {}
    for no, arg in enumerate(kwargs):
        try:
            key, value = arg.split("=", 1)
            key = key.encode(settings.DEFAULT_CHARSET)
        except Exception, e:
            return lucidTagNodeError(
                plugin_name, method_name,
                "The key word argument %s is not in the right format. (%s)" % (
                    cgi.escape(repr(arg)), e
                )
            )
        value = value.strip('"')
        method_kwargs[key] = value

    return lucidTagNode(plugin_name, method_name, method_kwargs)

