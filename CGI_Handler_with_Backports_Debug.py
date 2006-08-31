#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python v2.2 and v2.3!

with debugged application, sould be only used for testing!
"""

from __future__ import generators

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
import cgitb;cgitb.enable()
import sys

from PyLucid.python_backports import backports
from wsgiref.handlers import CGIHandler

from colubrid.debug import DebuggedApplication


if __name__ == "__main__":
    oldstdout = sys.stdout
    sys.stdout = sys.stderr

    # with 'debugged application':
    app = DebuggedApplication('PyLucid_app:app')

    # without 'debugged application':
    #~ from PyLucid_app import app

    sys.stdout = oldstdout

    CGIHandler().run(app)
