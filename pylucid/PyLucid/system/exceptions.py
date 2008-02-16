#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    PyLucid own Exception's

HTTP/1.1 - Status Code Definitions:
http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
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
