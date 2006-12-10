#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
config Middelware
"""

from PyLucid.system.exceptions import *
from PyLucid.system.exceptions_LowLevel import CGI_Error

try:
    import config # PyLucid Grundconfiguration aus "./config.py"
except ImportError, e:
    txt = (
        "No config.py exists. You must copy config-example.py to config.py and"
        " edit the database settings."
    )
    raise CGI_Error(e, txt)


class configMiddleware(object):
    """
    preferences Tabelle aus Datenbank lesen und als Dict zur verfügung stellen
    """

    def __init__(self, app):
        self.config_data = config.config
        self.app = app

    def __call__(self, environ, start_response):
        environ['PyLucid.config'] = self.config_data
        return self.app(environ, start_response)


