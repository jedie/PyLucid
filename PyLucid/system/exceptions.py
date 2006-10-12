#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's
"""


#~ __all__ = ["DBerror","ConnectionError","ProbablyNotInstalled"]


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
    a, h1 {
        color:#440;
    }
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
    def get_error_page(self):
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
    code = 500
    title = 'Database Error'

    def __init__(self, txt, origErrMsg=""):
        self.msg = (
            '<p>%s</p>\n'
            '<p><small>%s</small></p>\n'
            '<p>Have you install PyLucid? Please look at:'
            ' <a href="http://www.pylucid.org/index.py/InstallPyLucid/">'
            'PyLucid.org - Install</a></p>'
        ) % (txt, origErrMsg)




installInfo = (
    '<p>More info at:'
    ' <a href="http://www.pylucid.org/index.py/InstallAccess/">'
    'PyLucid.org - install access</a></p>'
)

class NoInstallLockFile(PyLucidException):
    """
    Der User möchte in die Install-Sektion, aber die InstallLock-Datei, mit
    dem Passwort, ist nicht vorhanden
    """
    code = 403
    title = 'Access denied.'
    msg = '<p>install lock file "install_lock.txt" not found!</p>'
    msg += installInfo

class WrongInstallLockCode(PyLucidException):
    """
    Falscher "install Lock Code" in der URL
    """
    code = 403
    title = 'Access denied.'

    def __init__(self, origErrMsg):
        self.msg = "<p>%s</p>\n%s" % (origErrMsg, installInfo)




class LogInError(PyLucidException):
    """
    Fehler beim Login
    """
    #~ code = 403
    # Mit 403 erhält man oft nur eine Apache-Fehlerseite und nicht
    # die hier generierte.
    # TODO: Abklären, warum man 403 nicht nehmen kann
    code = 500
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