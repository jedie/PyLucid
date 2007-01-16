#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's

HTTP/1.1 - Status Code Definitions:
http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
"""


__version__ = """
v0.1.2
    - Neue Methode get_error_page_msg() für ticket:3
v0.1.1
    - Bugfix: http://pylucid.net/trac/ticket/18
        - args fehlte als Attribut der Exception Klassen
v0.1
    - erste Version
"""

__ToDo__ = """
Apache and other error codes than 200 OK
"""


import cgi

from colubrid.exceptions import HttpException





ERROR_PAGE_TEMPLATE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>%(code)s %(title)s</title>
  <style type="text/css">
    html, body {
        padding: 30px;
        background-color: #FFE;
    }
    body {
        font-family: tahoma, arial, sans-serif;
        color: #000000;
        font-size: 0.9em;
        background-color: #FFFFDB;
        margin: 30px;
        border: 3px solid #C9C573;
    }
    form * {
      vertical-align:middle;
    }
    a, h1 {color:#440;}
    em {color:#a00;}
    div.content {
        margin: 1em 3em 2em 2em;
    }
    address {
        border-top: 1px solid #ccc;
        padding: 0.3em;
    }
  </style>
 </head>
 <body>
<h1>%(title)s</h1>
<div class="content">%(msg)s</div>
<address>powered by PyLucid</address>
</body></html>
"""


class PyLucidException(HttpException):
    """Base for HTTP exceptions. Not to be used directly."""
    args="[undefined args]" # FixMe: Warum muß es args hier geben???
    code=500
    msg="[undefined msg]"
    """
    args wird benötigt, wenn eine PyLucidException angafangen wird. z.b.:
        try:
            raise LogInError("TEST")
        except Exception, e:
            self.page_msg(Exception, e)
    """
    def __init__(self, code, args, msg):
        self.code = code
        self.args = args
        self.msg = msg

    def get_error_page_msg(self):
        """
        Der Fehler wird als page_msg Angezeigt und nicht als eigene Seite.
        Wird vom ModuleManager angefordert,
        wenn config.ModuleManager_error_handling = True
        """
        msg = "%s\n%s" % (self.title, self.msg)
        msg = msg.replace("<p>","")
        msg = msg.replace("</p>","\n")
        return msg

    def get_error_page(self):
        """
        Liefert die Fehler-HTML-Seite zurück, die colubrid dann anzeigt.
        """
        return ERROR_PAGE_TEMPLATE % {
            'code':     self.code,
            'title':    self.title,
            'msg':      self.msg,
        }

class DBerror(PyLucidException):
    """HTTP 404."""
    code = 500
    title = 'Database Error'

    def __init__(self, e, txt):
        self.msg = (
            "<p>%s</p>\n"
            "<p>%s</p>"
        ) % (txt, e)


class ConnectionError(PyLucidException):
    """HTTP 404."""
    code = 500
    title = 'Database Connection Error'

    def __init__(self, origErrMsg):
        self.msg = (
            "<p>%s</p>\n"
            "<p>Please Check your config.py!</p>"
        ) % origErrMsg



class ProbablyNotInstalled(PyLucidException):
    """
    Fehler die auftauchen, wenn PyLucid noch nicht installiert ist.
    Tritt auf, wenn versucht wird auf SQL-Daten zurück zu greifen, wenn
    die Tabellen überhaupt noch nicht eingerichtet wurden.
    """
    code = 200
    title = 'Database Error'

    def __init__(self, txt):
        self.msg = (
            '<h3>%s</h3>\n'
            '<h4>Have you install PyLucid?</h4>'
            '<p>Try: <a href="index.py/_install">'
            '  index.py/_install<em>InstallPassword</em></a></p>'
            '<p>(You find information about the PyLucid installation at:'
            '  <a href="http://www.pylucid.org/index.py/InstallPyLucid/">'
            '  PyLucid.org - Install</a>)'
            '</p>'
        ) % (txt)

class NoPageExists(PyLucidException):
    code = 200
    title = "No existing CMS page"

    def __init__(self, msg):
        self.msg = msg





INSTALL_INFO = (
    '<p>More info at:'
    ' <a href="http://www.pylucid.org/index.py/InstallAccess/">'
    'PyLucid.org - install access</a></p>'
)

class NoInstallLockFile(PyLucidException):
    """
    Der User möchte in die Install-Sektion, aber die InstallLock-Datei, mit
    dem Passwort, ist nicht vorhanden
    """
    code = 200
    title = 'Access denied.'

    def __init__(self):
        self.msg = '<p>install lock file "install_lock.txt" not found!</p>'
        self.msg += INSTALL_INFO

class WrongInstallLockCode(PyLucidException):
    """
    Falscher "install Lock Code" in der URL
    """
    code = 200
    title = 'Access denied.'

    def __init__(self, origErrMsg):
        self.msg = "<p>%s</p>\n%s" % (origErrMsg, INSTALL_INFO)







class LogInError(PyLucidException):
    """
    Fehler beim Login
    """
    #~ code = 403
    # Mit 403 erhält man oft nur eine Apache-Fehlerseite und nicht
    # die hier generierte.
    # TODO: Abklären, warum man 403 nicht nehmen kann
    code = 200
    title = 'Access denied.'

    def __init__(self, origErrMsg):
        self.msg = origErrMsg




class IntegrityError(Exception):
    """
    Fehler bei einer DB-Transaktion
    """
    pass

class WrongTemplateEngine(Exception):
    """
    Die Template-Engine ist falsch
    """
    pass
