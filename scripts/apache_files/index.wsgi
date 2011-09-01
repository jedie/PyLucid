#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid mod_wsgi dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    But create_page_instance.sh will do this for you, see:
        http://www.pylucid.org/permalink/355/1a2-create-a-new-page-instance

    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import sys
import time
import atexit
import traceback
import StringIO

#####################################################################################################
# PLEASE CHANGE THIS PATH:
#
os.environ["VIRTUALENV_FILE"] = "/please/insert/path/to/PyLucid_env/bin/activate_this.py"
#
# It's the absolute filesystem path to ...PyLucid_env/bin/activate_this.py
#
#####################################################################################################

# This must normaly not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

#DEBUG = True
DEBUG = False

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_PATH)

# Low level log file.
LOGFILE = os.path.join(BASE_PATH, "low_level_wsgi.log")

APP_ERROR = ""


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

if DEBUG:
    atexit.register(low_level_log, "-- END --")
    low_level_log("startup %r..." % __file__)


def tail_log(max=20):
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


def get_apache_load_files(path):
    """ Simply get a list of all *.load files from the path. """
    modules = []
    for item in os.listdir(path):
        filepath = os.path.join(path, item)
        if os.path.isfile(filepath):
            name, ext = os.path.splitext(item)
            if ext == ".load" and name not in modules:
                modules.append(name)
    return modules

def get_pylucid_ver():
    try:
        from pylucid_project import VERSION_STRING
        return VERSION_STRING
    except Exception, err:
        return "[Error: %s]" % err

def get_ip_info():
    try:
        import socket
        domain_name = socket.getfqdn()
    except Exception, err:
        domain_name = "[Error: %s]" % err
        ip_addresses = "-"
    else:
        try:
            ip_addresses = ", ".join(socket.gethostbyname_ex(domain_name)[2])
        except Exception, err:
            ip_addresses = "[Error: %s]" % err
    return ip_addresses, domain_name


def lowlevel_error_app(environ, start_response):
    """
    Fallback application, used to display the user some information, why the
    main app doesn't start.
    """
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield "<h1>PyLucid - Low level error ;( </h1>"

    yield "<h2>Last lines in %s</h2>" % LOGFILE
    yield "<pre>%s</pre>" % tail_log()

    global APP_ERROR
    yield "<h2>App traceback:</h2>"
    yield "<pre>%s</pre>" % APP_ERROR

    yield "<h2>System informations:</h2>"
    yield "<ul>"
    yield "<li>PyLucid v%s</li>" % get_pylucid_ver()
    yield "<li>Python v%s</li>" % sys.version
    yield "<li>sys.prefix: %r</li>" % sys.prefix
    yield "<li>__name__: %r</li>" % __name__
    yield "<li>os.uname: %r</li>" % " ".join(os.uname())
    yield "<li>PID: %s, UID: %s, GID: %s</li>" % (os.getpid(), os.getuid(), os.getgid())
    yield "<li>IPs: %s, Domain: %s</li>" % get_ip_info()
    yield "</ul>"

    from cgi import escape

    yield "<h2>Apache modules:</h2>"
    try:
        path = "/etc/apache2/mods-enabled"
        yield "<p><small>(load files from %r)</small><br />" % path
        modules = get_apache_load_files(path)
        yield ", ".join(sorted(modules))
        yield "</p>"
    except:
        yield "Error: %s" % traceback.format_exc()

    yield "<h2>Environment</h2>"

    yield "<h3>WSGI Environment</h3>"
    yield "<table>"
    for k, v in sorted(environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(repr(v)))
    yield "</table>"

    yield "<h3>OS Environment</h3>"
    yield "<table>"
    for k, v in sorted(os.environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(v))
    yield "</table>"

    yield "<h2>sys.path</h2>"
    yield "<ul>"
    for path in sys.path:
        yield "<li>%s</li>" % path
    yield "</ul>"

    yield "<h2>Try to run django app with CGI:</h2>"
    yield "<p>(You will see the raw, escaped response content or a traceback!)</p>"
    yield "<pre>"
    try:
        yield escape(run_django_cgi())
    except:
        yield "Error: %s" % traceback.format_exc()
    yield "</pre>"

    yield "<hr />"
    yield "<p>Low level traceback -- END --</p>"



def info_app(environ, start_response):
    low_level_log("startup info_app...")
    headers = []
    headers.append(('Content-Type', 'text/plain'))
    write = start_response('200 OK', headers)

    import cStringIO

    input = environ['wsgi.input']
    output = cStringIO.StringIO()

    print >> output, "PID: %s" % os.getpid()
    print >> output, "UID: %s" % os.getuid()
    print >> output, "GID: %s" % os.getgid()
    print >> output

    keys = environ.keys()
    keys.sort()
    for key in keys:
        print >> output, '%s: %s' % (key, repr(environ[key]))
    print >> output

    output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))

    return [output.getvalue()]



def get_wsgi_app():
    """ return pylucid WSGI app """
    activate_virtualenv()

    try:
        from django.conf import settings
    except:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import 'settings'!")
        raise etype, evalue, etb

    try:
        from django.core.handlers.wsgi import WSGIHandler
    except Exception, err:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Can't import django stuff: %s" % err)
        raise etype, evalue, etb

    return WSGIHandler()



class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application
    def __call__(self, environ, start_response):
        low_level_log("REQUEST: %s" % repr(environ))

        def _start_response(status, headers, *args):
            low_level_log("RESPONSE: %s %s" % (status, repr(headers)))
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)


try:
    # will only be present when running under Apache/mod_wsgi
    from mod_wsgi import version
except:
    low_level_log(
        "Seems we are not running under Apache/mod_wsgi (Original error: %s)" % traceback.format_exc()
    )
else:
    try:
        if DEBUG:
            application = LoggingMiddleware(get_wsgi_app())
        else:
            application = get_wsgi_app()
    except:
        # Catch the traceback and run a minimal wsgi debug application
        APP_ERROR = traceback.format_exc()
        low_level_log(APP_ERROR) # Write full traceback into LOGFILE
        application = lowlevel_error_app




