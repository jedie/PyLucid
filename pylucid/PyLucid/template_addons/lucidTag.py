# -*- coding: utf-8 -*-

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

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import cgi, re

from PyLucid.system.plugin_manager import run
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.context_processors import add_css_tag
from PyLucid.tools.data_eval import data_eval, DataEvalError
from PyLucid.tools.utils import make_kwargs

from django.conf import settings
from django import template


# FIXME: The re should be more fault-tolerant:
KWARGS_REGEX = re.compile('''(\w*?)\=['"](.*?)['"]''')

# Not all plugin output should surrounded with a <div> tag:
CSS_TAG_BLACKLIST = ("page_style", "RSSfeedGenerator",)


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

        if not self.plugin_name in CSS_TAG_BLACKLIST:
            content = add_css_tag(
                context, content, self.plugin_name, self.method_name
            )

        return content




def lucidTag(parser, token):
    """
    Parse the lucidTags.

    syntax e.g.:
        {% lucidTag PluginName %}
        {% lucidTag PluginName kwarg1="value1" %}
        {% lucidTag PluginName kwarg1="value1" kwarg2="value2" %}
    """
    raw_content = token.contents
    content = raw_content.split(" ", 2)[1:]
    plugin_name = content.pop(0)

    if "." in plugin_name:
        plugin_name, method_name = plugin_name.split(".", 1)
    else:
        method_name = "lucidTag"

    if content:
        raw_kwargs = content[0]
        method_kwargs = make_kwargs(raw_kwargs)
    else:
        method_kwargs = {}

    return lucidTagNode(plugin_name, method_name, method_kwargs)

