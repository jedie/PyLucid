#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
config Middelware
"""

from PyLucid.system.exceptions import *

import config # PyLucid Grundconfiguration aus "./config.py"


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


