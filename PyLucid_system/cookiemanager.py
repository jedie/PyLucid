#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__ = "0.0.2"

__history__ = """
v0.0.2
    - debug-Methode hinzugefügt
v0.0.1
    - erste Version
"""

import os
from Cookie import SimpleCookie

class cookie:
    def __init__( self ):
        self.cookieObj = SimpleCookie()
        self.load()

    def load( self ):
        if not os.environ.has_key("HTTP_COOKIE"):
            # Kein Cookie vorhanden
            return

        self.cookieObj.load( os.environ["HTTP_COOKIE"] )

    def readCookie( self, CookieName ):
        if self.cookieObj == False:
            # Gibt kein Cookie
            return False

        if self.cookieObj.has_key(CookieName):
            return self.cookieObj[CookieName].value
        else:
            return False

    def debug( self ):
        print "Cookie-Debug:"
        print "<hr><pre>"
        if not os.environ.has_key("HTTP_COOKIE"):
            print "There is no HTTP_COOKIE in os.environ:\n"
            for k,v in os.environ.iteritems(): print k,v
        else:
            print self.cookieObj
        print "</pre><hr>"

if __name__ == "__main__":
    cookie().debug()
