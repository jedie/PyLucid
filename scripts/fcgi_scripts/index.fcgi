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

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

#print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#print "Content-type: text/plain; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#import cgitb;cgitb.enable()

import os


#####################################################################################################
# CHANGE THIS PATH:
#
# The absolute filesystem path to ...PyLucid_env/bin/activate_this.py
#
os.environ["VIRTUALENV_FILE"] = "/path/to/PyLucid_env/bin/activate_this.py"
#
#####################################################################################################


# This must normaly not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


def traceback_end():
    """ Print out a traceback and terminate with sys.exit() """
    print
    print "-" * 80
    import sys
    print "Python v%s" % sys.version
    print "-" * 80
    try:
        import traceback
        print traceback.format_exc()
    except Exception, e:
        print "Error: %s" % e
    sys.exit()


try:
    virtualenv_file = os.environ["VIRTUALENV_FILE"]
except KeyError, err:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "environment variable VIRTUALENV_FILE not set!"
    print "(VIRTUALENV_FILE is the path to '.../PyLucid_env/bin/activate_this.py')"
    print
    traceback_end()


try:
    execfile(virtualenv_file, dict(__file__=virtualenv_file))
except Exception, err:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "VIRTUALENV_FILE value is wrong: %r" % virtualenv_file
    print
    print "Please edit the file %r and change the path!" % __file__
    print
    traceback_end()


try:
    from django.conf import settings
except:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "Can't import 'settings'!"
    print
    traceback_end()


try:
    from django.core.handlers.wsgi import WSGIHandler
    from django.core.servers.fastcgi import runfastcgi
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "<h1>Error:</h1><h2>Can't import django stuff:</h2>"
    print "<h3>%s</h3>" % e
    traceback_end()


try:
    #~ runfastcgi()
    runfastcgi(method="threaded", daemonize="false")
    #runfastcgi(socket="fcgi.sock", daemonize="false")
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "Low-Level-Error:", e
    print
    print "-" * 80
    print
    traceback_end()
