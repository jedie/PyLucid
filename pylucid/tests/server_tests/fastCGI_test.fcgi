#!/usr/bin/python2.4
# -*- coding: UTF-8 -*-

"""
    a low level fastCGI test
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Note:
    -You need the python package "flup": http://trac.saddi.com/flup

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, os

# Logging
#LOGFILE = None # No logging!
LOGFILE = "PyLucid_fcgi.log" # Log into this file


if LOGFILE:
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=LOGFILE,
        filemode='a'
    )
    log = logging.debug
    log("Logging started")
else:
    # No logging
    def log(*txt):
        pass


try:
    from flup.server.fcgi import WSGIServer
except ImportError, e:
    msg = "Import error: %s" % e
    log(msg)
    print >> sys.stderr, msg
    raise


try:
    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])

        from cgi import escape
        yield '<h1>FastCGI Environment</h1><table>'
        yield '<tr><th>%s</th><td>%s</td></tr>' % (
            escape(repr(k)), escape(repr(v))
        )

    WSGIServer(app).run()
except Exception, e:
    msg = "Run app error: %s" % e
    log(msg)
    print >> sys.stderr, msg
    raise
else:
    msg = "Application end."
    log(msg)
    print >> sys.stderr, msg
    raise