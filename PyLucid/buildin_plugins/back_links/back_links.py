#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
<lucidTag:back_links/>
Generiert eine horizontale zurück-Linkleiste

Created by Jens Diemer

GPL-License
"""



import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys, cgi, urllib

indexSide = "Start"

from PyLucid.system.BaseModule import PyLucidBaseModule

class back_links(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(back_links, self).__init__(*args, **kwargs)

        self.indexlink = '<a href="%s">Index</a>' % (
            self.URLs.pageLink("/")
        )

        self.backlink  = '<a href="%(url)s">%(title)s</a>'

        self.current_page_id  = self.request.session["page_id"]

    def lucidTag( self ):
        "Backlinks generieren"
        if self.current_page_id == self.preferences["core"]["defaultPageName"]:
            # Die aktuelle Seite ist die Index-Seite, also auch keinen
            # indexLink generieren
            return ""

        # aktuelle parent-ID ermitteln
        parent_id = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",self.current_page_id)
            )[0]["parent"]

        if parent_id == 0:
            # Keine Unterseite vorhanden -> keine back-Links ;)
            return self.indexlink

        try:
            # Link-Daten aus der DB hohlen
            data = self.backlink_data( parent_id )
        except IndexError, e:
            self.response.write("[back links error: %s]" % e)
            return

        self.make_links( data )

    def backlink_data( self, page_id ):
        """ Holt die Links von der aktuellen Seite bis zur Index-Seite aus der DB """
        data = []
        while page_id != 0:
            result = self.db.select(
                    select_items    = ["name","title","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result )

        # Liste umdrehen
        data.reverse()

        return data

    def make_links( self, data ):
        """ Generiert aus den Daten eine Link-Zeile """
        self.response.write(self.indexlink)

        oldurl = ""
        for link_data in data:
            url = oldurl + "/" + urllib.quote_plus(link_data["name"])
            oldurl = url
            url = self.URLs.pageLink(url)

            title = link_data["title"]
            if (title == None) or (title == ""):
                title = link_data["name"]

            link = self.backlink % {
                "url": url,
                "title": cgi.escape( title ),
            }
            self.response.write(" &lt; %s" % link)







