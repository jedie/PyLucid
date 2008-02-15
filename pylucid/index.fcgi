#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

"""
    PyLucid fastCGI dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
    some examples:
        #!/usr/bin/env python2.4
        #!/usr/bin/python2.4
        #!C:\python\python.exe

    Note:
    -If this file does not lie in the project folder, you must set PROJECT_DIR!
    -You need the python package "flup": http://trac.saddi.com/flup

    Debugging help
    ~~~~~~~~~~~~~~
    If you only see something like
        - "FastCGI Unhandled Exception"
        - "Internal Server Error"
        - "Premature end of script headers"
    try this:
        - Set a LOGFILE
        - use the runfastcgi() options:
            daemonize="false"
            maxrequests=1
        - Use ./tests/server_tests/fastCGI_test.fcgi
        - Try to turn on the flup traceback, see:
            http://code.djangoproject.com/ticket/6610

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
import sys, os, time

start_overall = time.time()

# Logging
# If you enable logging, you should set maxrequests=1 in the runfastcgi method
# above. Then you see a "alive" log entry (sysexit) afert every request.
LOGFILE = None # No logging!
#LOGFILE = "PyLucid_fcgi.log" # Log into this file

# Change into a other directory?
PROJECT_DIR = None # No chdir needed
#PROJECT_DIR = "/var/www/htdocs/pylucid/" # Change into this directory


# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

# Global variable for the last traceback:
last_tb_info = None

#______________________________________________________________________________
# Setup logging:

if LOGFILE:
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=LOGFILE,
        filemode='a'
    )
    log = logging.debug
    log("--- Logging started ---")
else:
    # No logging
    def log(*txt):
        pass

#______________________________________________________________________________
# redirect stderr if logging is on:

if LOGFILE:
    try:
        class StdErrorHandler(object):
            """
            redirects messages from stderr to stdout.
            Sends a header, if the header were not already sent.
            """
            def __init__(self, out_method):
                self.out_method = out_method

            def write(self, *txt):
                text = "".join([i for i in txt])
                for line in text.splitlines():
                    self.out_method(line)

        sys.stderr = StdErrorHandler(log)
        sys.stderr.write("stderr redirected into the logfile")
    except Exception, e:
        log("StdErrorHandler error: %s" % e)

#______________________________________________________________________________


def tb_catch_app(environ, start_response):
    """ Minimalistic WSGI app for debugging """
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield '<h1>FastCGI Traceback catch</h1>'

    # Display the overall running time
    yield 'overall time: %.2fsec' % (time.time() - start_overall)

    # Display the last traceback
    yield '<h2>last_tb_info:</h2>'
    try:
        yield "<pre>%s</pre>" % last_tb_info
    except Exception, e:
        yield "Traceback error: %s" % e

    yield '<hr />'

    from cgi import escape
    yield '<h1>FastCGI Environment</h1><table>'
    for k, v in sorted(environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (
            escape(repr(k)), escape(repr(v))
        )
    yield '</table>'

#______________________________________________________________________________
# If this file does not lie in the project folder, then you must define the
# path to the project directory here:

if PROJECT_DIR:
    # Switch to the directory of your project.
    log("chdir '%s'" % PROJECT_DIR)
    try:
        os.chdir(PROJECT_DIR)
    except Exception, e:
        log("chdir error:", e)

    # Add a custom Python path, you'll want to add the parent folder of
    # your project directory. (Optional.)
    try:
        sys.path.insert(0, PROJECT_DIR)
    except Exception, e:
        log("path.insert error:", e)

#______________________________________________________________________________

from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.fastcgi import runfastcgi

try:
    log('runfastcgi()')
    runfastcgi(
        #method="prefork",  # prefork or threaded (default prefork)
        #daemonize="false", # Bool, whether to detach from terminal
        #maxrequests=1,     # number of requests a child handles before it is
                            # killed and a new child is forked (0 = no limit)
        #maxspare=2,        # max number of spare processes/threads
        #maxchildren=2      # hard limit number of processes/threads
        #debug=True,        # Not Implemented, see:
                            # http://code.djangoproject.com/ticket/6610
    )
except SystemExit, e:
    log("sys.exit(%s) appears." % e)
except Exception, e:
    log("fastCGI error: %s" % e)
    import sys, traceback
    last_tb_info = traceback.format_exc()
    log(last_tb_info)
    from flup.server.fcgi import WSGIServer
    WSGIServer(tb_catch_app).run()
else:
    log("fastcgi application ended.")
