#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python v2.3!

with debugged application, sould be only used for testing!
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
import cgitb;cgitb.enable()
import sys


try:
    from PyLucid.system.exceptions_LowLevel import CGI_Error, CGI_main_info
except Exception, e:
    msg = "Can't import PyLucid.system.exceptions_LowLevel.CGI_Error: %s" % e
    print "Content-type: text/html; charset=utf-8\r\n\r\n"
    print "<h2>%s</h2>" % msg
    raise ImportError(msg)


# Backport for some Python v2.4 features (subprocess.py)
sys.path.insert(0,"PyLucid/python_backports")


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
        # with 'debugged application':
        app = DebuggedApplication('PyLucid_app:app')
    except Exception, e:
        raise CGI_Error(e, "Can't init DebuggedApplication!")

    try:
        CGIHandler().run(app)
    except Exception, e:
        raise CGI_Error(e, "Can't run the CGI-Handler!")

else:
    # Kann passieren, wenn das Skript nicht als CGI läuft, sondern
    # evtl. über mod_python
    CGI_main_info()