#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python 2.4!

with debugged application, sould be only used for testing!
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
import cgitb;cgitb.enable()
import sys


try:
    from PyLucid.system.exceptions_LowLevel import CGI_Error
except Exception, e:
    msg = "Can't import PyLucid.system.exceptions_LowLevel.CGI_Error: %s" % e
    print "Content-type: text/html; charset=utf-8\r\n\r\n"
    print "<h2>%s</h2>" % msg
    raise ImportError(msg)
    #~ print "Can't import PyLucid.system.exceptions.CGI_Error :"
    #~ print e


try:
    from wsgiref.handlers import CGIHandler
except Exception, e:
    raise CGI_Error(e, "Can't import wsgiref.handlers.CGIHandler!")


try:
    from colubrid.debug import DebuggedApplication
except Exception, e:
    raise CGI_Error(
        e, "Can't import colubrid.debug.DebuggedApplication!"
    )



if __name__ == "__main__":
    try:
        #~ oldstdout = sys.stdout
        #~ sys.stdout = sys.stderr

        # with 'debugged application':
        app = DebuggedApplication('PyLucid_app:app')

        # without 'debugged application':
        #~ from PyLucid_app import app

        #~ sys.stdout = oldstdout

    except Exception, e:
        raise CGI_Error(e, "Can't init DebuggedApplication!")

    CGIHandler().run(app)

else:
    # Kann passieren, wenn das Skript nicht als CGI läuft, sondern
    # evtl. über modPython
    print "<h1>Error:</h1>"
    print "<p>__name__ == %s (should be __main__!)</p>" % __name__
    gateway = os.environ.get(
        "GATEWAY_INTERFACE", "[Error: GATEWAY_INTERFACE not in os.environ!]"
    )
    if gateway!="CGI/1.1":
        print "<h3>Running not as CGI!</h3>"
        print "<p>You should use an other WSGI Handler!</p>"

    print "<p>GATEWAY_INTERFACE: <strong>%s</strong></p>" % gateway