# -*- coding: utf-8 -*-

"""
    {% lucidTag ... %}
    ~~~~~~~~~~~~~~~~~~

    the special PyLucid tag who starts a plugin with the plugin manager.
    e.g.: {% lucidTag plugin_name.method_name key1="value1" key2="value2" %}

    registered in: ./PyLucid/defaulttags/__init__.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import cgi
import shlex

#from PyLucid.system.plugin_manager import run
#from PyLucid.system.response import SimpleStringIO
#from PyLucid.system.context_processors import add_css_tag

from django.conf import settings
from django import template
from django.core.urlresolvers import get_callable


# FIXME: The re should be more fault-tolerant:
KWARGS_REGEX = re.compile('''(\w*?)\=['"](.*?)['"]''')

# TODO: Should be removed in the next release
CSS_TAG_BLACKLIST = getattr(
    settings, "CSS_TAG_BLACKLIST", ("page_style", "RSSfeedGenerator",)
)



# For make_kwargs()
KEYWORD_MAP = {
    "True": True,
    "False": False,
    "None": None,
}

def str2dict(raw_content):
    """
    convert a string into a dictionary. e.g.:

    >>> make_kwargs('key1="value1" key2="value2"')
    {'key2': 'value2', 'key1': 'value1'}

    >>> make_kwargs('A="B" C=1 D=1.1 E=True F=False G=None')
    {'A': 'B', 'C': 1, 'E': True, 'D': '1.1', 'G': None, 'F': False}
    
    >>> make_kwargs('''key1="'1'" key2='"2"' key3="""'3'""" ''')
    {'key3': 3, 'key2': 2, 'key1': 1}

    >>> make_kwargs(u'unicode=True')
    {'unicode': True}
    """
    if isinstance(raw_content, unicode):
        # shlex.split doesn't work with unicode?!?
        raw_content = raw_content.encode(settings.DEFAULT_CHARSET)

    parts = shlex.split(raw_content)

    result = {}
    for part in parts:
        key, value = part.split("=", 1)

        if value in KEYWORD_MAP:
            # True False or None
            value = KEYWORD_MAP[value]
        else:
            # A number?
            try:
                value = int(value.strip("'\""))
            except ValueError:
                pass

        result[key] = value

    return result




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
        # callback is either a string like 'foo.views.news.stories.story_detail'
        callback = "pylucid_plugins.%s.views.%s" % (self.plugin_name, self.method_name)
        callable = get_callable(callback)
        
        try:
            request = context["request"]
        except KeyError:
            raise KeyError("request object not in context! You must add it into the template context!")
        
        response = callable(request, **self.method_kwargs)
        return response
        return cgi.escape("%s - %s" % (self.__repr__(), repr(callable)))
        
#        local_response = SimpleStringIO()
#        output = run(
#            context, local_response,
#            self.plugin_name, self.method_name,
#            method_kwargs = self.method_kwargs
#        )
#        if output == None:
#            content = local_response.getvalue()
#        elif isinstance(output, basestring):
#            content = output
#        else:
#            msg = (
#                "Error: Wrong output from inline Plugin!"
#                " - It should be write into the response object and return None"
#                " or return a basestring!"
#                " - But %s.%s has returned: %s (%s)"
#            ) % (
#                self.plugin_name, self.method_name,
#                repr(output), type(output)
#            )
#            raise AssertionError(msg)
#
#        if not self.plugin_name in CSS_TAG_BLACKLIST:
#            content = add_css_tag(
#                context, content, self.plugin_name, self.method_name
#            )
#
#        return content




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
        method_kwargs = str2dict(raw_kwargs)
    else:
        method_kwargs = {}

    return lucidTagNode(plugin_name, method_name, method_kwargs)

