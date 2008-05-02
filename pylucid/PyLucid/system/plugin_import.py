# -*- coding: utf-8 -*-
"""
    PyLucid Plugin Manager
    ~~~~~~~~~~~~~~~~~~~~~~

    The plugin manager starts a plugin an returns the content back.
    For _command requests and for {% lucidTag ... %}

    install/Deintstall plugins into the database.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


def _import(from_name, object_name, debug):
    """
    from 'from_name' import 'object_name'
    """
    try:
        return __import__(from_name, {}, {}, [object_name])
    except (ImportError, SyntaxError), e:
        if debug:
            raise
        raise ImportError, "Can't import %s from %s: %s" % (
            object_name, from_name, e
        )

def get_plugin_module(package_name, plugin_name, debug):
    plugin_module = _import(
        from_name = ".".join([package_name, plugin_name, plugin_name]),
        object_name = plugin_name,
        debug = debug,
    )
    return plugin_module

#    debug = request.user.is_superuser or request.debug


def debug_plugin_config(page_msg, plugin_config):
    for item in dir(plugin_config):
        if item.startswith("_"):
            continue
        page_msg("'%s':" % item)
        page_msg(getattr(plugin_config, item))

def get_plugin_config(package_name, plugin_name, debug, extra_verbose=False):
    """
    imports the plugin and the config plugin and returns a merge config-object

    dissolve_version_string == True -> get the version string (__version__)
        from the plugin and put it into the config object
    """
    config_name = "%s_cfg" % plugin_name
    from_name = ".".join([package_name, plugin_name, config_name])
    if extra_verbose:
        print "from %s import %s" % (from_name, config_name)

    config_plugin = _import(from_name, config_name, debug)

    return config_plugin

def get_plugin_version(package_name, plugin_name, debug):
    plugin_plugin = get_plugin_module(package_name, plugin_name, debug)

    plugin_version = getattr(plugin_plugin, "__version__", "")

    # Cleanup a SVN Revision Number
    plugin_version = plugin_version.strip("$ ")

    return plugin_version






