# -*- coding: utf-8 -*-

"""
    PyLucid own exceptions
    ~~~~~~~~~~~~~~~~~~~~~~

    HTTP/1.1 - Status Code Definitions:
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

class AccessDenied(Exception):
    """
    e.g. anonymous tries to view a cms page without permitViewPublic flag.
    """
    pass

class PluginError(Exception):
    """
    For every error in a Plugin how should be displayed into the cms page.
    TODO: Catch this error in the plugin manager!
    """
    pass

class LowLevelError(Exception):
    """
    A low level error was raised. PyLucid can't work. In the PyLucid common
    middleware this exception would be catched and the install_info.html
    template would be send to the user.
    """
    pass

class PluginPreferencesError(Exception):
    pass