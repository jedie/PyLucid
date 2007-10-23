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
    If this file does not lie in the project folder, you must use custom_path()!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='/tmp/pylucid.log',
    filemode='a'
)
logging.debug('Starting up 2')
import sys, os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def custom_path(dir):
    # Switch to the directory of your project.
    os.chdir(directory)

    # Add a custom Python path, you'll want to add the parent folder of
    # your project directory. (Optional.)
    sys.path.insert(0, directory)


#______________________________________________________________________________
# If this file does not lie in the project folder, then you must define the
# path to the project directory here:

#custom_path("/path/to/your/project/direcotry/")

#______________________________________________________________________________


# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.fastcgi import runfastcgi

#~ old_stderr = sys.stderr
#~ sys.stderr = StringIO

def tb_catch_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield '<h1>FastCGI Traceback catch:</h1>'

    global msg
    yield "<pre>"
    yield msg
    yield "</pre>"
    yield "stderr output:<pre>"
    yield stderr_output
    yield "</pre>"

    stderr_output = sys.stderr.getvalue()
    logging.error(stderr_output)


try:
    #~ raise SystemError("Test!")
    #~ runfastcgi()
    runfastcgi(method="threaded", daemonize="false")
    #runfastcgi(socket="fcgi.sock", daemonize="false")
except:
    import traceback
    msg = traceback.format_exc()
    logging.error(msg)
    from flup.server.fcgi import WSGIServer
    WSGIServer(tb_catch_app).run()
else:
    msg = "Error: Nothings happens?!?!"
    logging.error(msg)
    from flup.server.fcgi import WSGIServer
    WSGIServer(tb_catch_app).run()
