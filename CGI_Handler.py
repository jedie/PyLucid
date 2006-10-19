#!/usr/bin/python -O
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python 2.4, without 'debugged application'!

You can rename this file! For example to 'index.py'
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
#~ import cgitb;cgitb.enable()

from wsgiref.handlers import CGIHandler
from PyLucid_app import app

CGIHandler().run(app)