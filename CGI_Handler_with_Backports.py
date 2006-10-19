#!/usr/bin/python -OO
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python v2.3, without 'debugged application'!

You can rename this file! For example to 'index.py'
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
#~ import cgitb;cgitb.enable()
import sys

# Backport for some Python v2.4 features (subprocess.py)
sys.path.insert(0,"PyLucid/python_backports")

from wsgiref.handlers import CGIHandler

from PyLucid_app import app

CGIHandler().run(app)