
# -*- coding: utf-8 -*-

"""
    PyLucid fastCGI server
    ~~~~~~~~~~~~~~~~~~~~~~

    Try to catch all errors and display them with the tb_catch_app().

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import sys, os, time

#os.environ["FCGI_FORCE_CGI"] = "y"

# For displaing the complete running time in tb_catch_app()
start_overall = time.time()

# Global variable for the last traceback:
last_tb_info = None

def fake_logging(*txt):
    """ fake function for no logging """
    pass

def setup_logging(logfile):
    """
    logging
    returns a log function that should be called for every log statement.
    """
    if not logfile:
        # No logging -> return a fake log function
        return fake_logging

    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=logfile,
        filemode='a'
    )
    log = logging.debug
    log("--- Logging started ---")

    return log


def redirect_strerr(log):
    """
    redirect stderr into the log file
    """
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


def setup_project_dir(project_dir, log):
    """
    If this file does not lie in the project folder, we change the current
    workdir and insert it to the sys.path
    """
    current_dir = os.getcwd()
    if not project_dir:
        log("Use current workdir '%s'" % current_dir)
        return

    log("Change current workdir '%s' to '%s'" % (current_dir, project_dir))

    # Switch to the directory of your project.
    os.chdir(project_dir)

    # Add a custom Python path, you'll want to add the parent folder of
    # your project directory. (Optional.)
    sys.path.insert(0, project_dir)

#______________________________________________________________________________


def tb_catch_app(environ, start_response):
    """
    Minimalistic WSGI app for debugging
    """
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield '<h1>FastCGI Traceback catch</h1>\n'

    # Display the overall running time
    yield 'overall time: %.2fsec\n' % (time.time() - start_overall)

    # Display the last traceback
    yield '<h2>last_tb_info:</h2>\n'
    try:
        global last_tb_info
        yield "<pre>%s</pre>\n" % last_tb_info
    except Exception, e:
        yield "Traceback error: %s\n" % e

    yield '<hr />\n'

    from cgi import escape
    yield '<h1>FastCGI Environment</h1><table>\n'
    for k, v in sorted(environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>\n' % (
            escape(repr(k)), escape(repr(v))
        )
    yield '</table>'


def lowlevel_traceback(log=None):
    """
    -build a formated last traceback info
    -run tb_catch_app who display the last traceback info
    """
    try:
        global last_tb_info
        import traceback
        last_tb_info = traceback.format_exc()
        if log:
            log(last_tb_info)

        from flup.server.fcgi_fork import WSGIServer
        WSGIServer(
            tb_catch_app, multithreaded=False, debug=True,
            maxRequests=1, maxSpare=1, maxChildren=1
        ).run()
    except SystemExit, e:
        log("sys.exit(%s) appears2." % e)
    except Exception, e:
        log("lowlevel_traceback() error: %s" % e )


def start_app(log, runfastcgi_kwargs):
    """
    Run the django app
    """
    from django.core.handlers.wsgi import WSGIHandler
    from django.core.servers.fastcgi import runfastcgi

    log('runfastcgi(kwargs=%s)' % runfastcgi_kwargs)
    return runfastcgi(**runfastcgi_kwargs)


#______________________________________________________________________________


def fastcgi_server(project_dir=None, logfile=None,
                    settings_module="PyLucid.settings", runfastcgi_kwargs={}):
    """
    setup the environement and startup fastcgi.
    """
    log=fake_logging # If a traceback raised in setup_logging()
    try:
        log = setup_logging(logfile)

        if logfile: # Only redirect stderr output, if logging is on.
            redirect_strerr(log)

        setup_project_dir(project_dir, log)

        # Set the DJANGO_SETTINGS_MODULE environment variable.
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

        #----------------------------------------------------------------------
        # overide the given runfastcgi kwargs

        # prefork or threaded (default prefork)
        #~ runfastcgi_kwargs["method"]="prefork"

        # "true" or "false" whether to detach from terminal
        # Importand: It's not a bool, it's a string!
        #~ runfastcgi_kwargs["daemonize"]="false"

        # number of requests a child handles before it is killed and a new child
        # is forked (0 = no limit)
        #~ runfastcgi_kwargs["maxrequests"]=1

        # max number of spare processes/threads
        #~ runfastcgi_kwargs["maxspare"]=2

        # hard limit number of processes/threads
        #~ runfastcgi_kwargs["maxchildren"]=2

        # Not Implemented, see: http://code.djangoproject.com/ticket/6610
        runfastcgi_kwargs["debug"]=True

        #----------------------------------------------------------------------

        succeeds = start_app(log, runfastcgi_kwargs)
    except SystemExit, e:
        log("sys.exit(%s) appears." % e)
    except Exception, e:
        log("fastCGI error: %s" % e)
        lowlevel_traceback(log)
    else:
        log("fastcgi application ended, returned: %s" % succeeds)

