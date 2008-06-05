#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    Note:
    -If this file does not lie in the project folder, you must set project_dir.
    -You need the python package "flup": http://trac.saddi.com/flup

    Debugging help
    ~~~~~~~~~~~~~~
    If you only see something like
        - "FastCGI Unhandled Exception"
        - "Internal Server Error"
        - "Premature end of script headers"
    try this:
        - Set a logfile
        - use the runfastcgi() options:
            daemonize="false"
            maxrequests=1
        - Use ./tests/server_tests/fastCGI_test.fcgi
        - Try to turn on the flup traceback, see:
            http://code.djangoproject.com/ticket/6610

    Give feedback in our forum!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from PyLucid.system.fastcgi_server import fastcgi_server

fastcgi_server(
    # Change into a other project directory?
    # (default: not set -> Don't change the current workdir)
    # e.g.:
    # project_dir="/var/www/htdocs/pylucid/",

    # Logging
    # If you enable logging, you should set "maxrequests"=1 and
    # "daemonize":"false" in runfastcgi_kwargs. Then you see a "alive" log
    # entry (sysexit) after every request.
    # (default: not set -> No logging)
    # e.g.:
    #logfile="PyLucid_fcgi.log",

    # The DJANGO_SETTINGS_MODULE environment variable.
    # (default: "PyLucid.settings")
    settings_module="PyLucid.settings",

    # Keyword arguments for django.core.servers.fastcgi.runfastcgi()
    # (default: empty dict, no options set)
    runfastcgi_kwargs={
        # prefork or threaded (default "prefork")
        #"method": "prefork",

        # "true" or "false" whether to detach from terminal
        # Importand: It's not a bool, it's a string!
        #"daemonize": "false",

        # Number of requests a child handles before it is killed and a new
        # child is forked.
        # (default: 0 -> no limit)
        # Set to 1 for debugging
        #"maxrequests":1,

        # max number of spare processes/threads
        #"maxspare":2,

        # hard limit number of processes/threads
        #"maxchildren":2,

        # Not Implemented, see: http://code.djangoproject.com/ticket/6610
        #"debug":True,
    }
)