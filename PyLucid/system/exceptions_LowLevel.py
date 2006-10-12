#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's for Low Level Error's

Hier sind Exceptions, getrennt von exceptions.py, weil keine Abhängikeiten
mit colubrid hier sein dürfen. Damit es 'immer' funktioniert.
Wichtig z.B. bei Python 2.2 (ohne datetime!), dabei kann nicht der colubrid
gemacht werden:

from colubrid.exceptions import HttpException

(Dabei kommt es zu einem "ImportError: No module named datetime" :(
"""

class CGI_Error(Exception):
    """
    LowLevel-Fehler sind fehler, die schon beim Handler auftreten!
    Nur für CGI!
    """
    def __init__(self, e, txt):
        print "Content-type: text/html; charset=utf-8\r\n\r\n"
        print "<h1>PyLucid - Low Level Error:</h1>"
        print "<h3>%s</h3>" % txt
        print "<h4>%s</h4>" % e
        print "<hr />"
        msg = "PyLucid Low Level Error: %s - %s" % (txt, e)

        # In die Apache Log schreiben (?):
        import sys
        sys.stderr.write(msg)

        # Ob das wohl Sinn macht?
        raise SystemExit(msg)