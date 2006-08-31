#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Der Parser füllt eine CMS Seite mit leben ;)
Parsed die lucid-Tags/Funktionen, führt diese aus und fügt das Ergebnis in die
Seite ein.
"""

__version__="0.1.4"

__history__="""
v0.1.4
    - apply_markup kommt mit markup id oder richtigen namen klar
v0.1.3
    - textile Parser erhält nun auch die PyLucid-Objekt. page_msg ist
        hilfreich zum debuggen des Parsers ;)
v0.1.2
    - Bug 1297263:
        "Can't use textile-Markup (maximum recursion limit exceeded)":
        Nun wird zuerst das Markup angewendet und dann erst die lucidTag's
        aufgelöst
v0.1.1
    - parser.handle_function(): toleranter wenn kein String vom Modul zurück
        kommt
    - Versionsnummer geändert
v0.1.0
    - Erste Version: Komplett neugeschrieben. Nachfolge vom pagerender.py
"""

__todo__ = """
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber
die Seiten keine IDs, sondern die richtigen Namen verwenden geht das leider
noch nicht :(
"""

import sys, cgi, re, time



class render(object):
    """
    Parsed die Seite und wendes das Markup an.
    """
    def init2(self, request, response):
        self.request = request
        self.response = response

        #shorthands
        self.session        = request.session
        self.db             = request.db
        self.staticTags     = request.staticTags
        self.preferences    = request.preferences
        self.tools          = request.tools
        self.page_msg       = response.page_msg

    def write_page_template(self):
        """ Baut die Seite zusammen """

        page_id = self.session["page_id"]
        page_data = self.db.get_side_data(page_id)
        self.staticTags.fill_with_page_data(page_data)

        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def write_command_template(self):
        # FIXME - Quick v0.7 Patch !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def get_rendered_page(self, page_id):
        page = self.db.get_content_and_markup(page_id)
        #~ self.page_msg(page)
        content = self.apply_markup(
            content = page["content"],
            markup = page["markup"]
        )
        return content

    def apply_markup(self, content, markup):
        """
        Wendet das Markup auf den Seiteninhalt an
        """
        if markup == "textile":
            # textile Markup anwenden
            if self.preferences["ModuleManager_error_handling"] == True:
                try:
                    from PyLucid.system import tinyTextile
                    out = self.tools.out_buffer()
                    t = tinyTextile.parser(out, self.request, self.response)
                    t.parse(content)
                    return out.get()
                except Exception, e:
                    msg = "Can't use textile-Markup (%s)" % e
                    self.page_msg(msg)
                    return msg
            else:
                from PyLucid.system import tinyTextile
                out = self.tools.out_buffer()
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg("Markup '%s' not supported yet :(" % markup)
            return content

