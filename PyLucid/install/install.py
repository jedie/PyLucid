#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid "installer"


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""



import os, sys, cgi, urllib

from PyLucid.system.exceptions import *

# Colubrid
from colubrid import ObjectApplication




installLockFilename = "install_lock.txt"



HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta http-equiv="expires"      content="0" />
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
html, body {
    padding: 30px;
    background-color: #FFFFEE;
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
input {
    border: 1px solid #C9C573;
    margin: 0.4em;
}
pre {
    background-color: #FFFFFF;
    padding: 1em;
}
#menu li, #menu li a {
    list-style-type: none;
    padding: 0.3em;
}
#menu h4 {
    margin: 0px;
}
a {
    color:#0BE;
    padding: 0.1em;
}
a:hover {
    color:#000000;
    background-color: #F4F4D2;
}
</style>
%(addCodeTag)s
</head>
<body>
<h3>%(info)s - Setup @ <a href="%(base_url)s">%(base_url)s</a></h3>
<lucidTag:page_msg/>
"""
HTML_bottom = """
<hr />
<small>
<p>Rendertime: <lucidTag:script_duration/></p>
</small>
</body></html>"""




from PyLucid.install import menu
from PyLucid.install.ObjectApp_Base import ObjectApp_Base

from PyLucid.install.App_tests import tests
from PyLucid.install.App_Update import update
from PyLucid.install.App_LowLevelAdmin import LowLevelAdmin
from PyLucid.install.App_ScratchInstall import install





class InstallApp(object):
    """
    Klasse die die Programmlogik zusammenstellt
    """
    charset = 'utf-8'
    slash_append = False

    root = menu.menu
    root.install        = install
    root.update         = update
    root.LowLevelAdmin  = LowLevelAdmin
    root.tests          = tests

    def __init__(self, request, response):
        self.request = request
        self.response = response

        # Shorthands
        self.environ        = self.request.environ
        self.db             = self.request.db
        self.preferences    = self.request.preferences
        self.URLs           = self.request.URLs
        self.tools          = self.request.tools
        self.page_msg       = self.response.page_msg

        self.LockCodeURL, self.PathInfo = self.prepareInstallPathInfo()

    #_________________________________________________________________________

    def prepareInstallPathInfo(self):
        path = self.environ["PATH_INFO"]
        #~ self.page_msg(path)
        parts = path.split('/')

        parts = [i for i in parts if i!=""]

        #~ self.page_msg(parts)

        LockCodeURL = parts[0]
        PathInfo = parts[1:]

        return LockCodeURL, PathInfo

    #_________________________________________________________________________

    def process_request(self):
        """ request abarbeiten """

        try:
            self.checkLock()
        except SystemExit:
            # Keine lock-Datei vorhanden -> abbruch
            return

        self.writeHTMLhead()

        # Die Basisklasse für die einzelnen Module vorbereiten
        self.setup_ObjectApp_Base()

        # Eigentliche Methode wird aufgerufen
        self.startObjectApp()

        #~ self.response.write("TEST")
        #~ return self.response

        self.writeHTMLfoot()

    #_________________________________________________________________________

    def checkLock(self):
        """
        Schaut nach, ob der URL-lock-Code mit dem aus der
        Datei übereinstimmt
        """

        try:
            f = file(installLockFilename, "rU")
            lockCode = f.readline()
            f.close()
        except IOError, e:
            if os.path.isfile(installLockFilename):
                # Die Datei existiert, kann aber nicht geöffnet werden
                raise WrongInstallLockCode(
                    "Can't open '%s': %s" % (installLockFilename, e)
                )
            else:
                raise NoInstallLockFile

        lockCode = lockCode.strip() # Leerzeichen wegschneiden

        #~ print "Debug: |%s| <-> |%s|" % (self.LockCodeURL, lockCode)

        if len(lockCode)<8:
            raise WrongInstallLockCode(
                "Install lock code to short! (len min. 8 chars!)"
            )

        if not self.LockCodeURL.endswith(lockCode):
            raise WrongInstallLockCode("Wrong install lock code in URL!")

    #_________________________________________________________________________

    def setup_ObjectApp_Base(self):
        """
        Bereitet die ObjectApp_Base-Klasse vor
        (von dieser erben alle ObjApp-Module)
        """

        # Menügenerator "einpflanzen"
        ObjectApp_Base.MenuGenerator = menu.Install_MenuGenerator(
            self.response, self.root,
            base_path = self.environ.get('APPLICATION_REQUEST', ''),
            blacklist = ("response",)
        )

        # response und request einpflanzen
        ObjectApp_Base.response = self.response
        ObjectApp_Base.request  = self.request

        # Shorthands übergeben
        ObjectApp_Base._db              = self.db
        ObjectApp_Base._page_msg        = self.page_msg


        ObjectApp_Base._preferences     = self.preferences

        ObjectApp_Base._environ         = self.environ
        ObjectApp_Base._URLs            = self.URLs
        ObjectApp_Base._tools           = self.tools

        #~ self.URLs.debug()

    #_________________________________________________________________________

    def writeHTMLhead(self):
        """ HTML Kopf schreiben """
        head = HTML_head % {
            "info": self.__info__,
            "base_url": self.URLs.absoluteLink("/"),

            # Schreibt den addCode-Tag, damit am Ende noch die CSS/JS Daten
            # von Modulen eingefügt werden können
            "addCodeTag": self.response.addCode.tag,
        }
        self.response.write(head)

    def writeHTMLfoot(self):
        """ HTML Fuss schreiben """
        self.response.write(HTML_bottom)

    #_________________________________________________________________________

    def startObjectApp(self):
        """
        Ruft die Methode auf, anhand von PATH_INFO

        Fast das selbe wie colubrid.application.ObjectApplication !
        """
        # Resolve the path
        handler = self.root
        args = []
        for part in self.PathInfo:
            node = getattr(handler, part, None)
            if node is None:
                if part:
                    args.append(part)
            else:
                handler = node

        #~ container = None

        # Find handler and make first container check
        import inspect
        if inspect.ismethod(handler):
            if handler.__name__ == 'index':
                # the handler is called index so it's the leaf of
                # itself. we don't want a slash, even if forced
                container = False
        else:
            index = getattr(handler, 'index', None)
            if index == None:
                msg = (
                    "Module/Method unknown, check requestet path: %s"
                ) % self.PathInfo
                raise AttributeError(msg)


            if not hasattr(index, 'container'):
                container = True
            handler = index

        for arg in args:
            try:
                arg = int(arg)
            except ValueError:
                continue

        # call handler
        parent = handler.im_class()
        parent.request = self.request
        try:
            handler(parent, *args)
        #~ except TypeError, e:
            #~ msg = (
                #~ "Error execute install ObjApp Subaction '%s': %s"
            #~ ) % (handler.__name__, e)
            #~ raise TypeError, msg
        except SystemExit, e:
            # sys.exit() wird immer bei einem totalabbruch gemacht ;)
            self.response.write('<small style="color:grey">(exit %s)</small>' % e)





