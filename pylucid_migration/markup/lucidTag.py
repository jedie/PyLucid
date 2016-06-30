# coding: utf-8

"""
    {% lucidTag ... %}
    ~~~~~~~~~~~~~~~~~~

    the special PyLucid tag who starts a plugin with the plugin manager.
    e.g.: {% lucidTag plugin_name.method_name key1="value1" key2="value2" %}


    FIXME: ERROR parse lucidTag in line: '{% lucidTag IncludeRemote url, title=None, preformat=None, escape=True %}':

        File "/home/jens/PyLucid_env/src/pylucid/pylucid_migration/markup/lucidTag.py", line 33, in str2dict
            key, value = part.split("=", 1)
        ValueError: need more than 1 value to unpack


    :copyleft: 2007-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import sys
import shlex
import traceback

# FIXME: The re should be more fault-tolerant:
KWARGS_REGEX = re.compile('''(\w*?)\=['"](.*?)['"]''')


# For str2dict()
KEYWORD_MAP = {
    "True": True,
    "False": False,
    "None": None,
}

def str2dict(content):
    parts = shlex.split(content)
    result = {}
    for part in parts:
        try:
            key, value = part.split("=", 1)
        except Exception as err:
            print("Error splitting %r: %s" % (part, err))
            raise

        value=value.strip("'\"")

        if value in KEYWORD_MAP:
            # True False or None
            value = KEYWORD_MAP[value]
        else:
            # A number?
            try:
                value = int(value)
            except ValueError:
                pass

        result[key] = value

    return result



def parse_lucidtag(raw_content):
    """
    Parse the lucidTags.

    syntax e.g.:
        {% lucidTag PluginName %}
        {% lucidTag PluginName kwarg1="value1" %}
        {% lucidTag PluginName.MethodName kwarg1="value1" kwarg2="value2" %}
    """
    assert raw_content.startswith("{%")
    assert raw_content.endswith("%}")
    content = raw_content[2:-2].strip()

    try:
        # e.g.: {% lucidTag PluginName kwarg="value" %}
        method_name, plugin_name, content = content.split(" ", 2)
    except ValueError:
        # e.g.: {% lucidTag update_journal %}
        method_name, plugin_name = content.split(" ")
        method_kwargs = {}
    else:
        method_kwargs = str2dict(content)

    assert method_name=="lucidTag"

    if "." in plugin_name:
        plugin_name, method_name = plugin_name.split(".", 1)

    return plugin_name, method_name, method_kwargs



if __name__ == "__main__":
    content='{% lucidTag IncludeRemote url="http://members.ebay.de/aboutme/eBayUserName" title="eBay about me page" %}'
    result = parse_lucidtag(content)
    print(result)
    assert result == (
        'IncludeRemote', 'lucidTag',
        {
            'url': 'http://members.ebay.de/aboutme/eBayUserName',
            'title': 'eBay about me page'
        }
    )

    content='{% lucidTag PluginName.MethodName kwarg1="value1" kwarg2="value2" %}'
    result = parse_lucidtag(content)
    print(result)
    assert result == (
        'PluginName', 'MethodName',
        {
            'kwarg1': 'value1',
            'kwarg2': 'value2'
        }
    )

    content ='{% lucidTag update_journal %}'
    result = parse_lucidtag(content)
    print(result)
    assert result == ('update_journal', 'lucidTag', {})