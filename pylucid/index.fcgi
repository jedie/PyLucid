#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid fastCGI dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os

from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.fastcgi import runfastcgi

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

# Add a custom Python path, you'll want to add the parent folder of
# your project directory. (Optional.)
#BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#import sys
#sys.path.insert(0, BASE_PATH)

# Switch to the directory of your project. (Optional.)
#os.chdir(BASE_PATH)

def tb_catch_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield '<h1>FastCGI Traceback catch:</h1>'

    global msg
    yield "<pre>"
    yield msg
    yield "</pre>"

try:
    #runfastcgi()
    runfastcgi(method="threaded", daemonize="false")
    #runfastcgi(socket="fcgi.sock", daemonize="false")
except Exception, err1:
    import traceback
    msg = traceback.format_exc()

    from flup.server.fcgi import WSGIServer
    WSGIServer(tb_catch_app).run()
else:
    msg = "Error: Nothings happends?!?!"
    from flup.server.fcgi import WSGIServer
    WSGIServer(tb_catch_app).run()
