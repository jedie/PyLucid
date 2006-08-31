#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python v2.2 and v2.3, without 'debugged application'!

You can rename this file! For example to 'index.py'
"""

from __future__ import generators

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
#~ import cgitb;cgitb.enable()
#~ from colubrid.debug import DebuggedApplication

import sys

from PyLucid.python_backports import backports
from wsgiref.handlers import CGIHandler


if __name__ == "__main__":
    oldstdout = sys.stdout
    sys.stdout = sys.stderr

    # with 'debugged application':
    #~ app = DebuggedApplication('PyLucid_app:app')

    # without 'debugged application':
    from PyLucid_app import app

    sys.stdout = oldstdout

    CGIHandler().run(app)
