# -*- coding: utf-8 -*-

"""
    PyLucid Plugin Import
    ~~~~~~~~~~~~~~~~~~~~~~

    Functions around the plugin import:
        - get_plugin_module()
        - get_plugin_config()
        - get_plugin_version()

        - debug_plugin_config()


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# internal import functions

def import2(from_name, object_name=[]):
    """
    generic function for import
    from 'from_name' import 'object_name'
    """
    obj = __import__(from_name, fromlist=[object_name])
    if object_name == []:
        return obj

    try:
        return getattr(obj, object_name)
    except AttributeError:
        raise AttributeError(
            "'%s' object has no attribute '%s" % (obj.__name__, object_name)
        )


def _import(from_name, object_name, debug):
    """
    import function with error handling, used import2()
    from 'from_name' import 'object_name'
    """
    try:
        # unicode -> string
        from_name = str(from_name)
        object_name = str(object_name)

        return import2(from_name, object_name)
    except (ImportError, SyntaxError), err:
        if debug:
            raise
        raise ImportError, "Can't import %s from %s: %s" % (
            object_name, from_name, err
        )

#______________________________________________________________________________
# GET function

def get_plugin_module(package_name, plugin_name, debug):
    """
    imports the plugin module and returns the module object.
    """
    from_name = package_name + "." + plugin_name,
    object_name = plugin_name

    plugin_module = _import(from_name, object_name, debug)
    return plugin_module


def get_plugin_config(package_name, plugin_name, debug):
    """
    imports the plugin and the config plugin and returns a merge config-object
    """
    from_name = package_name + "." + plugin_name
    config_name = plugin_name + "_cfg"

    config_plugin = _import(from_name, config_name, debug)
    return config_plugin


def get_plugin_version(package_name, plugin_name, debug):
    """
    Returns the plugin version string.
    """
    plugin_plugin = get_plugin_module(package_name, plugin_name, debug)
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


