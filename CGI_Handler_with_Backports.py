#!/usr/bin/python -O
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python v2.3, without 'debugged application'!

You can rename this file! For example to 'index.py'
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
#~ import cgitb;cgitb.enable()
#~ from colubrid.debug import DebuggedApplication

import sys

# Backport for some Python v2.4 features (subprocess.py)
sys.path.insert(0,"PyLucid/python_backports")

from wsgiref.handlers import CGIHandler


if __name__ == "__main__":
    oldstdout = sys.stdout
    sys.stdout = sys.stderr

    # with 'debugged application':
    #~ app = DebuggedApplication('PyLucid_app:app')

    # without 'debugged application':
    from PyLucid_app import app

    sys.stdout = oldstdout

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