# -*- coding: utf-8 -*-

"""
    PyLucid Plugin Import
    ~~~~~~~~~~~~~~~~~~~~~~

    Functions around the plugin import:
        - get_plugin_module()
        - get_plugin_config()
        - get_plugin_version()

        - debug_plugin_config()

    TODO: Merge all methods into the plugin model/manager:
        http://pylucid.net:8080/pylucid/ticket/200

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

#______________________________________________________________________________
# internal import functions

def import2(from_name, fromlist=None, globals={}, locals={}):
    """
    A easy __import__ function.
    TODO: Python 2.5 level argument not supported, yet.
    Link: http://www.python-forum.de/topic-14591.html (de)

    >>> import sys
    >>> sys2 = import2("sys")
    >>> sys is sys2
    True

    >>> from time import time
    >>> time2 = import2("time", "time")
    >>> time is time2
    True

    >>> from os.path import sep
    >>> sep2 = import2("os.path", "sep")
    >>> sep is sep2
    True

    >>> from os import sep, pathsep
    >>> sep2, pathsep2 = import2("os", ["sep", "pathsep"])
    >>> sep is sep2 ; pathsep is pathsep2
    True
    True

    >>> import2("existiertnicht")
    Traceback (most recent call last):
        ...
    ImportError: No module named existiertnicht

    >>> import2("os", "gibtsnicht")
    Traceback (most recent call last):
        ...
    AttributeError: 'os' object has no attribute 'gibtsnicht
    """

    if isinstance(fromlist, basestring):
        # Only one from objects name
        fromlist = [fromlist]

    obj = __import__(from_name, globals, locals, fromlist)
    if fromlist==None:
        # Without a fromlist
        return obj

    # get all 'fromlist' objects
    result = []
    for object_name in fromlist:
        try:
            result.append(getattr(obj, object_name))
        except AttributeError, e:
            msg = "'%s' object has no attribute '%s" % (
                obj.__name__, object_name
            )
            raise AttributeError(msg)

    if len(result) == 1:
        return result[0]
    else:
        return result






def _import(from_name, object_name):
    """
    Thin layer aroung import2():
      - other error handling: raise original error or always a ImportError
      - catch SyntaxError, too (e.g. developing a PyLucid plugin)
      - convert unicode to string (Names from database are always unicode and
        the __import__ function must get strings)

    >>> from time import time
    >>> time2 = _import(u"time", u"time")
    >>> time is time2
    True

    >>> _import(u"A", u"B")
    Traceback (most recent call last):
        ...
    ImportError: Can't import 'B' from 'A': No module named A
    """
    try:
        # unicode -> string
        from_name = str(from_name)
        object_name = str(object_name)

        return import2(from_name, object_name)
    except (ImportError, SyntaxError), err:
        raise ImportError, "Can't import '%s' from '%s': %s" % (
            object_name, from_name, err
        )

#______________________________________________________________________________
# GET function

def get_plugin_module(package_name, plugin_name):
    """
    imports the plugin module and returns the module object.

    >>> get_plugin_module("A", "B")
    Traceback (most recent call last):
        ...
    ImportError: Can't import 'B' from 'A.B': No module named A.B
    """
    from_name = package_name + "." + plugin_name
    object_name = plugin_name

    plugin_module = _import(from_name, object_name)
    return plugin_module


def get_plugin_config(package_name, plugin_name):
    """
    imports the plugin and the config plugin and returns a merge config-object

    >>> get_plugin_config("A", "B")
    Traceback (most recent call last):
        ...
    ImportError: Can't import 'B_cfg' from 'A.B': No module named A.B
    """
    from_name = package_name + "." + plugin_name
    config_name = plugin_name + "_cfg"

    config_plugin = _import(from_name, config_name)
    return config_plugin


def get_plugin_version(package_name, plugin_name):
    """
    Returns the plugin version string.
    """
    try:
        plugin_plugin = get_plugin_module(package_name, plugin_name)
    except ImportError, err:
        raise ImportError("Can't get plugin version number: %s" % err)

    plugin_version = getattr(plugin_plugin, "__version__", "")

    # Cleanup a SVN Revision Number
    plugin_version = plugin_version.strip("$ ")
    return plugin_version

#______________________________________________________________________________
# DEBUG

def debug_plugin_config(page_msg, plugin_config):
    """
    Display the plugin config via page_msg
    """
    for item in dir(plugin_config):
        if item.startswith("_"):
            continue
        page_msg("'%s':" % item)
        page_msg(getattr(plugin_config, item))



if __name__ == "__main__":
    print "runnint doctest for %s" % __file__
    verbose = False
#    verbose = True
    import doctest
    doctest.testmod(verbose=verbose)
    print "--- END ---"