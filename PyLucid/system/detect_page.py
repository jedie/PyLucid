#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Durch poormans_modrewrite ist es nicht ganz so einfach festzustellen, welche
Seite die aktuelle ist :)


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"

import urllib, cgi

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.system.exceptions import *


#~ debug = True
debug = False



class detect_page(PyLucidBaseModule):
    """
    Legt die page ID der aktuellen Seite fest.
    Speichert die ID als "page_id"-Key in den Session-Daten,
    also: request.session["page_id"]
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(detect_page, self).__init__(*args, **kwargs)

    def detect_page(self):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if "page_id" in self.request.args:
            # Bei Modulen kann die ID schon in der URL mitgeschickt werden.
            self.check_page_id(self.request.args["page_id"])
            return

        pathInfo = self.environ.get("PATH_INFO","/")

            #~ if "page_id" in self.session:
                #~ self.check_page_id(self.session["page_id"])
                #~ return

            #~ self.set_history_page()
            #~ return


        self.check_page_name(pathInfo)
        return

        # Es konnte keine Seite in URL-Parametern gefunden werden, also
        # wird die Standart-Seite genommen
        #~ self.set_default_page()

    def check_page_id( self, page_id ):
        """ Testet ob die page_id auch richtig ist """
        try:
            db_page_id = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["id"]
        except IndexError:
            pass
        else:
            if db_page_id == page_id:
                # Alles OK
                return

        self.page_msg("404 Not Found. Page with id '%s' unknown." % page_id)
        self.set_default_page()

    def set_history_page( self ):
        if "page_history" in self.session:
            self.session["page_id"] = self.session["page_history"][0]
            self.check_page_id(self.session["page_id"])
        else:
            if debug:
                self.page_msg( "Debug: History nicht vorhanden!" )
            self.set_default_page()

    def check_page_name(self, page_name):
        """ ermittelt anhand des page_name die page_id """

        # /bsp/und%2Foder/ -> bsp/und%2Foder
        page_name = page_name.strip("/")

        if page_name == "":
            # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
            self.set_default_page()
            return


        # bsp/und%2Foder -> ['bsp', 'und%2Foder']
        page_name_split = page_name.split("/")


        if self.runlevel.is_command():
            # Ein internes Kommando (LogIn, EditPage ect.) wurde aufgerufen
            try:
                page_id = page_name_split[1]
            except ValueError:
                self.set_default_page()
                return

            self._set_page_id(page_id)
            return

            print "XXX:", page_id, "|||", page_name_split


        if len(page_name_split) == 1:
            self._singleShortcut(page_name_split[0])
        else:
            self._mutipleShortcut(page_name_split)

    def _singleShortcut(self, shortcut):
        """
        Es ist nur ein Shortcut in der URL

        Entweder befindet sich der User wirklich auf der ersten
        Ebene, oder aber es ist ein "kurz-Link" zu einer Seite die in einer
        tieferen Ebene ist!
        """
        try:
            page_id = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("shortcut",shortcut)
            )[0]["id"]
        except Exception,e:
            if debug:
                self.page_msg("_singleShortcut-Error:", e)
            self._error404(shortcut)
            self.set_default_page()
        else:
            self._set_page_id(page_id)

    def _mutipleShortcut(self, page_name_split):
        """
        Es sind mehrere Shortcut in der URL -> Der User befindet sich in
        einer Ebene >1
        Jeder einzelne Shortcut wird überprüft, ob die Seite existiert.
        """
        correctShortcuts=[]
        page_id = 0
        for no, shortcut in enumerate(page_name_split):
            try:
                page_id = self.db.select(
                    select_items    = ["id","parent"],
                    from_table      = "pages",
                    where           = [
                        ("shortcut",shortcut), ("parent",page_id)
                    ]
                )[0]["id"]
            except Exception,e:
                if debug:
                    self.page_msg("_mutipleShortcut-Error:", e)
                wrongShortcuts = page_name_split[no:]
                self._error404("/".join(wrongShortcuts))

                if no == 0:
                    # Kein Teil der URL ist richtig
                    self.set_default_page()
                else:
                    # Die ersten Teile der URL sind richtig, also werden diese
                    # berücksichtig
                    # URLs richtig setzten, damit die generierung von Links
                    # auch die richtige Grundlage haben:
                    self.URLs.handle404errors(correctShortcuts, wrongShortcuts)
                return
            else:
                correctShortcuts.append(shortcut)

        self._set_page_id(page_id)

    def _set_page_id(self, page_id):
        self.session["page_id"] = int(page_id)

        # Aktuelle Seite zur page_history hinzufügen:
        self.session.set_pageHistory(self.session["page_id"])

    def _error404(self, url):
        msg = (
            "404 Not Found."
            " The requested URL '%s' was not found on this server."
        ) % cgi.escape(url)
        self.page_msg(msg)

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        try:
            self.session["page_id"] = \
                                    self.preferences["core"]["defaultPageName"]
        except KeyError:
            self.page_msg(
                "Can'r read preferences from DB.",
                "(Did you install PyLucid correctly?)"
            )
            self.session["page_id"] = 0
        try:
            self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ["id",self.session["page_id"]]
            )[0]["id"]
        except IndexError:
            # Die defaultPageName Angabe ist falsch
            self.page_msg(
                "default Page with ID %s not found!" % self.session["page_id"]
            )
            try:
                self.session["page_id"] = self.db.select(
                    select_items    = ["id"],
                    from_table      = "pages",
                    order           = ("id","ASC"),
                    limit           = (0,1) # Nur den ersten ;)
                )[0]["id"]
            except IndexError:
                # Es gibt wohl überhaupt keine Seite???
                raise NoPageExists("No page in DB.")

        if debug:
            self.page_msg(
                "set_default_page(): ID %s" % self.session["page_id"]
            )