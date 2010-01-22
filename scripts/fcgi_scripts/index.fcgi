#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid fastCGI dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
        some examples:
            #!/usr/bin/env python
            #!/usr/bin/env python2.4
            #!/usr/bin/env python2.5
            #!/usr/bin/python
            #!/usr/bin/python2.4
            #!/usr/bin/python2.5
            #!C:\python\python.exe

    You must change the variable VIRTUALENV_FILE here!


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import sys
import time
import traceback
import StringIO


#####################################################################################################
# PLEASE CHANGE THIS PATH:
#
os.environ["VIRTUALENV_FILE"] = "please/insert/path/to/PyLucid_env/bin/activate_this.py"
#
# It's the absolute filesystem path to ...PyLucid_env/bin/activate_this.py
#
#####################################################################################################


# This must normaly not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


# Low level log file. Only created if the fastCGI app can't start.
LOGFILE = "low_level_fcgi.log"


def low_level_log(msg):
    """ append >msg< into LOGFILE """
    try:
        msg = "%s - %s\n" % (time.ctime()[4:-4], msg)
        f = open(LOGFILE, 'a')
        f.write(msg)
        f.close()
        sys.stderr.write(msg)
    except Exception, err:
        sys.stderr.write("Error, creating %r: %s" % (LOGFILE, err))


def tail_log(max=7):
    """ returns the last >max< lines, from LOGFILE """
    try:
        f = file(LOGFILE, "r")
        seekpos = -80 * max
        try:
            f.seek(seekpos, 2)
        except IOError: # File is to small
            pass
        last_lines = "".join(f.readlines()[-max:])
        f.close()
        return last_lines
    except:
        return "Error, getting %r content:\n%s" % (
            LOGFILE, traceback.format_exc()
        )




def activate_virtualenv():
    """
    Activate the virtualenv by execute the .../bin/activate_this.py
    """
    try:
        virtualenv_file = os.environ["VIRTUALENV_FILE"]# = "not exist!"
    except KeyError, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("environment variable VIRTUALENV_FILE not set!")
        raise etype, evalue, etb

    try:
        execfile(virtualenv_file, dict(__file__=virtualenv_file))
    except Exception, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype(
            (
                "VIRTUALENV_FILE value is wrong: %r"
                " - Please edit the file %r and change the path!"
            ) % (virtualenv_file, __file__)
        )
        raise etype, evalue, etb


def run_django_cgi():
    """
    Try to run the django app via CGI, using wsgiref (exist since Python v2.5)
    returns the raw response content.
    """
    activate_virtualenv()

    from wsgiref.handlers import CGIHandler
    from django.core.handlers.wsgi import WSGIHandler

    os.environ['REQUEST_METHOD'] = "GET"
    os.environ['REMOTE_ADDR'] = "localhost"
    os.environ['SERVER_NAME'] = "low level fastCGI test %r" % __file__
    os.environ['SERVER_PORT'] = "80"

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    buffer = StringIO.StringIO()
    sys.stdout = buffer
    sys.stderr = buffer
    try:
        CGIHandler().run(WSGIHandler())
        return buffer.getvalue()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        buffer.close()


def lowlevel_error_app(environ, start_response):
    """
    Fallback fastcgi application, used to display the user some information, why the
    main app doesn't start.
    """
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield "<h1>PyLucid - Low level error ;( </h1>"
    yield "<p>Python v%s</p>" % sys.version
    from cgi import escape

    yield "<h3>FastCGI Environment</h3>"
    yield "<table>"
    for k, v in sorted(os.environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(v))
    yield "</table>"

    yield "<h2>Last lines in %s</h2>" % LOGFILE
    yield "<pre>%s</pre>" % tail_log()

    yield "<h2>Try to run django app with CGI:</h2>"
    yield "<p>(You will see the raw, escaped response content or a traceback!)</p>"
    yield "<pre>"
    try:
        yield escape(run_django_cgi())
    except:
        yield "Error: %s" % traceback.format_exc()
    yield "</pre>"

    yield "<p><small>Low level traceback - END</small></p>"


def run_django_fcgi():
    """
    run the django app with django.core.servers.fastcgi.runfastcgi
    turn flup debug on, if settings.DEBUG is on.
    """
    activate_virtualenv()

    try:
        from django.conf import settings
    except:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import 'settings'!")
        raise etype, evalue, etb

    try:
        from django.core.handlers.wsgi import WSGIHandler
        from django.core.servers.fastcgi import runfastcgi
    except Exception, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import django stuff: %s" % err)
        raise etype, evalue, etb

    runfastcgi(
        method="threaded", daemonize="false",
        debug=settings.DEBUG # Enable flup debug
    )


try:
    run_django_fcgi()
except:
    # Catch the traceback and run a minimal fcgi debug application

    low_level_log(traceback.format_exc()) # Write full traceback into LOGFILE

    try:
        # http://trac.saddi.com/flup/browser/flup/server/fcgi.py
        from flup.server.fcgi import WSGIServer
        WSGIServer(lowlevel_error_app, debug=True).run()
    except:
        low_level_log(
            "Can't start lowlevel_error_app: %s" % traceback.format_exc()
        )


