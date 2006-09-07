#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verwaltung der verfügbaren URLs
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.2.1"

__history__="""
v0.2.1
    - debug() - wahlweise auch nach response statt nach page_msg
    - optimierungen bei pageLink()
    - neu: absoluteLink() (z.B. für RSS Generator)
    - neu: self.URLs["absoluteIndex"]
v0.2
    - currentAction kann nun auch args entgegen nehmen
v0.1
    - erste Version
"""


import os, posixpath, urllib




class URLs(dict):
    """
    Stellt Pfad-Informationen zu verfügung. Bietet Methoden zum zusammenbauen
    von URLs an.
    -verwaltet als Dict nur statische Pfade, die sich innerhalb eines
        Requests nicht verändern
    -Pfad-Methoden für dynamische Pfade!
    """
    def __init__(self, request, response):
        dict.__init__(self)
        self.lock = False

        self["command"] = None # Wird vom Module-Manager festgelegt
        self["action"] = None # Wird vom Module-Manager festgelegt

        # shorthands
        self.request        = request
        self.response       = response
        self.environ        = request.environ
        self.runlevel       = request.runlevel
        self.preferences    = request.preferences
        self.page_msg       = response.page_msg

        self._setup_pathInfo()

        # Alle "eigenen" URLs generieren
        self.setup_URLs()

        self.lock = True

    def _setup_pathInfo(self):
        """
        Liefert eine bearbeitete Version von environ['PATH_INFO'] zurück:
            - Ohne sub-Action-Parameter
            - Keine URL-GET-Parameter
            - als unicode
        """
        if "PATH_INFO" in self.environ:
            pathInfo = self.environ["PATH_INFO"]
        else:
            pathInfo = ""
            self.environ["PATH_INFO"] = ""

        if "?" in pathInfo:
            pathInfo, self["queryString"] = pathInfo.split("?",1)
        else:
            self["queryString"] = None

        pathInfo = pathInfo.strip("/")

        pathInfo = urllib.unquote(pathInfo)
        try:
            pathInfo = unicode(pathInfo, "utf-8")
        except:
            pass

        #~ self.environ['PATH_INFO'] = pathInfo
        self["pathInfo"] = pathInfo

    def addSlash(self, path):
        """
        >>> addSlash("/noSlash")
        '/noSlash/'
        >>> addSlash("/hasSlash/")
        '/hasSlash/'
        """
        if path[-1]=="/":
            return path
        else:
            return path+"/"

    def setup_URLs(self):
        """
        Pfad für Links festlegen

        Als Regeln gilt:
            - Alle Pfade ohne Slash am Ende
        """
        self["hostname"] = "%s://%s" % (
            self.environ.get('wsgi.url_scheme', "http"),
            self.environ['HTTP_HOST'],
        )

        self["scriptRoot"] = self.environ.get("SCRIPT_ROOT", "/")

        self["absoluteIndex"] = self["hostname"] + self["scriptRoot"]

    def setup_runlevel(self):
        """
        Bei _command oder _install wird path_info aufgeteilt.

        Statt /_install/tests/table_info/columns/lucid_pages
        ----> self["pathInfo"] = /_install/tests/table_info
        ----> self["actionArgs"] = ["columns", "lucid_pages"]
        """
        self.lock = False
        self["commandBase"] = posixpath.join(
            self["scriptRoot"], self.preferences["commandURLprefix"]
        )

        if self.runlevel.is_normal():
            self.lock = True
            return

        path = self["pathInfo"].split("/")

        if self.runlevel.is_install():
            self["commandBase"] = posixpath.join(
                self["scriptRoot"], path[0]
            )
            try:
                self["command"] = path[1]
            except IndexError:
                self["command"] = None
            else:
                try:
                    self["action"] = path[2]
                except IndexError:
                    self["action"] = None

        self["pathInfo"] = "/".join(path[:3])
        self["actionArgs"] = path[3:]

        self.lock = True


    def handle404errors(self, correctShortcuts, wrongShortcuts):
        """
        Wurde beim Aufruf eine teilweise falsche URL benutzt, werden zumindest
        die richtigen Teile verwendet.
        (wird von detect_page aufgerufen)
        """
        self.lock = False
        self["pathInfo"] = "/".join(correctShortcuts)
        self.lock = True
        return


    def items(self):
        """
        Überschreibt das items() von dict, um eine Reihenfolge zu erwirken
        """
        temp = []
        for k,v in self.iteritems():
            try:
                temp.append((len(v),k,v))
            except TypeError:
                # z.B. bei v == None ;)
                temp.append((0,k,v))

        temp.sort()

        result = []
        for _,k,v in temp:
            result.append((k,v))

        return result

    #_________________________________________________________________________

    def __setitem__(self, item, value):
        """ Nur für Debuging!!! """
        if self.lock == False:
            dict.__setitem__(self, item, value)
            return

        msg = ""
        try:
            import inspect
            # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            filename = inspect.stack()[1][1].split("/")[-1][-20:]
            msg += "%s, line %3s" % (filename, inspect.stack()[1][2])
        except Exception, e:
            msg += "<small>(inspect Error: %s)</small> " % e

        raise SystemError, (
            "URLs.__setitem__ forbidden!"
            " --- from '%s' --- item:'%s', value:'%s'"
        ) % (msg, item, value)

    #_________________________________________________________________________

    def pageLink(self, url):
        link = self.__make_link(self["scriptRoot"], url)
        return link

    def absoluteLink(self, url):
        link = self.__make_link(
            self["hostname"] + self["scriptRoot"], url
        )
        return link

    def __make_link(self, base, url):
        if url[0] == "/": # .lstrip("/") gibt es in Python 2.2 so nicht
            url = url[1:]

        link = posixpath.join(base, url)
        link = self.addSlash(link)
        return link

    def commandLink(self, modulename, methodname=""):
        #~ if self.runlevel.is_install():
            #~ link = posixpath.join(
                #~ self["scriptRoot"], self["commandBase"],
                #~ modulename, methodname
            #~ )
        #~ else:
            #~ link = posixpath.join(
                #~ self["commandBase"], modulename, methodname
            #~ )

        link = posixpath.join(
            self["commandBase"], modulename, methodname
        )

        link = self.addSlash(link)
        return link

    def actionLink(self, methodname, args=""):
        args = self._prepage_args(args)
        if self.runlevel.is_command():
            link = posixpath.join(
                self["scriptRoot"], self.preferences["commandURLprefix"],
                self["command"], methodname, args
            )
        elif self.runlevel.is_install():
            if self["command"] == None:
                # Wir sind im root also /_install/ ohne Kommando
                self.actionLinkRuntimeError("actionLink()")
            link = posixpath.join(
                self["scriptRoot"], self["commandBase"], self["command"],
                methodname, args
            )
        else:
            self.actionLinkRuntimeError("actionLink() wrong runlevel!")

        link = self.addSlash(link)
        return link

    def currentAction(self, args=""):
        args = self._prepage_args(args)
        if self.runlevel.is_command():
            link = posixpath.join(
                self["scriptRoot"], self.preferences["commandURLprefix"],
                self["command"], self['action'], args
            )
        elif self.runlevel.is_install():
            if self["command"] == None:
                # Wir sind im root also /_install/ ohne Kommando
                self.actionLinkRuntimeError("currentAction()")
            link = posixpath.join(
                self["scriptRoot"], self["pathInfo"], args
            )
        else:
            self.actionLinkRuntimeError("currentAction() wrong runlevel!")

        link = self.addSlash(link)
        return link

    def actionLinkRuntimeError(self, e):
        msg = (
            "Action link is only available if there is a action\n"
            ", but there is nothing! \n"
            "command: '%s', action: '%s' (runlevel: '%s', Error: %s)"
        ) % (self["command"], self['action'], self.runlevel.state, e)
        raise RuntimeError, msg

    def _prepage_args(self, args):
        if isinstance(args, list):
            args = "/".join(args)
        return args

    #_________________________________________________________________________
    # install Links

    def installSubAction(self, action):
        url = posixpath.join(
            self["scriptRoot"], self["pathInfo"], action
        )
        return url

    def installBaseLink(self):
        url = posixpath.join(
            self["scriptRoot"], self["commandBase"]
        )
        return url

    #_________________________________________________________________________

    def debug(self, response_out=False):

        #~ self.response.debug()
        def out(*txt):
            if response_out:
                self.response.write("%s\n" % " ".join([str(i) for i in txt]))
            else:
                self.page_msg(*txt)


        try:
            import inspect
            # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            filename = inspect.stack()[1][1].split("/")[-1][-20:]
            fileinfo = "%s, line %3s" % (filename, inspect.stack()[1][2])
        except Exception, e:
            fileinfo = "(inspect error: '%s')" % e

        out("path debug [%s]:" % fileinfo)
        out('request.runlevel:', self.runlevel)
        out('environ["PATH_INFO"]:', self.environ["PATH_INFO"])
        out('environ["SCRIPT_ROOT"]:', self.environ["SCRIPT_ROOT"])
        #~ for k,v in self.iteritems():
            #~ out(k,v)
        #~ out(self)
        for k,v in self.items():
            out(" - %15s: '%s'" % (k,v))

    #_________________________________________________________________________

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError, e:

            try:
                import inspect
                # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
                frameInfo = inspect.stack()[1]
                fileinfo = "...%s, line %3s" % (
                    frameInfo[1][-30:], frameInfo[2]
                )
            except Exception, e:
                fileinfo = "(inspect error: '%s')" % e
            msg = (
                "Key %s not exists in URLs (from %s)!"
                " --- Here the URLs dict: %s"
            ) % (
                e, fileinfo, self
            )
            raise KeyError, msg











