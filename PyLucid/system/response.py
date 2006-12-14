#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erweitert das colubrid response Objekt um ein paar Methoden.

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


# Colubrid
from colubrid import HttpResponse

import sys, os, re, cgi





lucidSplitRE = re.compile("<lucid(.*?)")

ignore_tag = ("page_msg", "script_duration")




class HttpResponse(HttpResponse):
    """
    Den original HttpResponse von colubrid erweitern, sodas alle
    PyLucid-Tags beim schreiben vom ModuleManager ausgef�llt werden
    """

    def write(self, txt):
        #~ if not isinstance(self.response, list):
            #~ raise TypeError('read only or dynamic response object')

        #~ if not isinstance(txt, basestring):
            #~ raise TypeError('str or unicode required')

        txt = lucidSplitRE.split(txt)
        for part in txt:
            if part.startswith("Tag:"):
                # Bsp part => Tag:page_body/><p>jau</p>

                tag, post = part.split(">",1)
                # tag  => Tag:page_body/
                # post => <p>jau</p>

                tag = tag[4:].rstrip("/")
                #~ if tag[-1]=="/": # .rstrip("/") gibt es in Python 2.2 so nicht
                    #~ tag = tag[:-1]

                # Tag über Module-Manager ausführen
                self.handleTag(tag)

                # Teil hinter dem Tag schreiben
                self.response.append(post)
            elif part.startswith("Function:"):
                # Bsp part:
                # Function:IncludeRemote>http://www.google.de</lucidFunction><p>jau</p>

                try:
                    function, post = part.split("</lucidFunction>",1)
                    # function  => Function:IncludeRemote>http://www.google.de
                    # post      => <p>jau</p>
                except ValueError:
                    # Der End-Tag wurde vergessen -> work-a-round
                    function, post = part.split(">",1)
                    function = function.split(":")[1]
                    function_info = None
                    self.page_msg(
                        "End tag not found for lucidFunction '%s'" % function
                    )
                else:
                    function, function_info = function.split(">")
                    # function      => Function:IncludeRemote
                    # function_info => http://www.google.de

                    function = function.split(":")[1]
                    # function => IncludeRemote

                self.module_manager.run_function(function, function_info)

                # Teil hinter dem Tag schreiben
                self.response.append(post)
            else:
                self.response.append(part)

    def handleTag(self, tag):
        if tag in ignore_tag:
            self.response.append("<lucidTag:%s/>" % tag)
        elif tag in self.staticTags:
            self.response.append(self.staticTags[tag])
        else:
            self.module_manager.run_tag(tag)

    def get(self):
        "zurückliefern der bisher geschriebene Daten"
        content = self.response
        # FIXME: unicode-Fehler sollten irgendwie angezeigt werden!
        result = ""
        for line in content:
            if type(line)!=unicode:
                line = unicode(line, errors="replace")
            result += line

        self.response = []
        return result

    def startFileResponse(self, filename, contentLen=None, \
                    content_type='application/octet-stream; charset=utf-8'):
        """
        Gibt einen Header aus, um einen octet-stream zu "erzeugen"

        Bsp:
        self.response.startFileResponse(filename, buffer_len)
        self.response.write(content)
        return self.response
        """
        if sys.platform == "win32":
            # force Windows input/output to binary
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        self.response = [] # Evtl. schon gemachte "Ausgaben" verwerfen
        print "reset:", self.response

        self.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        if contentLen:
            self.headers['Content-Length'] = '%s' % contentLen
        self.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        self.headers['Content-Type'] = content_type

    def startFreshResponse(self, content_type='text/html; charset=utf-8'):
        """
        Eine neue leere Seite ausgeben

        Bsp:
        self.response.startFreshResponse()
        self.response.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
            ' "xhtml1-strict.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '<head><title>BSP</title></head>\n'
            '<body><h1>Text</h1></body></html>\n'
        )
        return self.response
        """
        self.response = [] # Evtl. schon gemachte "Ausgaben" verwerfen
        self.headers['Content-Type'] = content_type




class staticTags(dict):
    """
    Dict zum speichern der statischen Tag-Informationen
    """

    def init2(self, request, response):
        # Shorthands
        self.environ        = request.environ
        self.runlevel       = request.runlevel
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.session        = request.session
        self.tools          = request.tools

    def setup(self):
        """
        "Statische" Tag's definieren
        """
        self["commandURLprefix"] = self.preferences["commandURLprefix"]
        self["installURLprefix"] = self.preferences["installURLprefix"]

        self["powered_by"]  = __info__

        self.setup_login_link()

        if self.runlevel.is_command():
            # Ein Kommando soll ausgeführt werden
            self.setup_command_tags()

    def setup_login_link(self):
        #~ if self.session.has_key("user") and self.session["user"] != False:
        if self.session != None and self.session["user"] != False:
            link = self.URLs.commandLink("auth", "logout")
            self["script_login"] = '<a href="%s">logout [%s]</a>' % (
                link, self.session["user"]
            )
        else:
            link = self.URLs.commandLink("auth", "login")
            self["script_login"] = '<a href="%s">login</a>' % (link)


    def setup_command_tags(self):
        self["robots"] = self.preferences["robots_tag"]["internal_pages"]
        self["page_keywords"] = ""
        self["page_description"] = ""

        #FIXME:
        self["page_name"] = self["page_title"] = self.environ["PATH_INFO"]
        self["page_last_modified"] = ""
        self["page_datetime"] = ""


    def fill_with_page_data(self, page_data):
        """
        Eintragen von Tags durch die CMS-Seiten-Informationen aus der DB
        Wird von page_parser.render verwendet
        """
        self["robots"] = self.preferences["robots_tag"]["content_pages"]

        self["markup"]               = page_data["markup"]
        self["page_name"]            = cgi.escape(page_data["name"])
        self["page_title"]           = cgi.escape(page_data["title"])
        self["page_keywords"]        = page_data["keywords"]
        self["page_description"]     = page_data["description"]

        self["page_last_modified"]   = self.tools.convert_date_from_sql(
            page_data["lastupdatetime"], format = "preferences"
        )

        self["page_datetime"]        = self.tools.convert_date_from_sql(
            page_data["lastupdatetime"], format = "DCTERMS.W3CDTF"
        )

