#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
-Parsen der Seite und wendet das Markup an.
-Schnittstelle zu Pygments

ToDo:
-----
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber
die Seiten keine IDs, sondern die richtigen Namen verwenden geht das leider
noch nicht :(
------------------------------------------------------------------------------

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

import sys, cgi, re, time

from PyLucid.tools.OutBuffer import OutBuffer



class render(object):

    def init2(self, request, response):
        self.request = request
        self.response = response

        #shorthands
        self.session        = request.session
        self.db             = request.db
        self.staticTags     = request.staticTags
        self.preferences    = request.preferences
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
        if isinstance(markup, int):
            markup = self.db.get_markup_name(markup)

        if markup == "textile":
            #~ self.page_msg("Debug: use textile")
            # textile Markup anwenden
            if self.preferences["ModuleManager_error_handling"] == True:
                #~ try:
                from PyLucid.system import tinyTextile
                out = OutBuffer(self.page_msg)
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
                #~ except Exception, e:
                    #~ msg = "Can't use textile-Markup (%s)" % e
                    #~ self.page_msg(msg)
                    #~ return msg
            else:
                from PyLucid.system import tinyTextile
                out = OutBuffer(self.page_msg)
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg("Markup '%s' not supported yet :(" % markup)
            return content

    def highlight(self, ext, code, out_object=None, pygments_style=None):
        #~ self.page_msg(args, kwargs)
        #~ self.request.module_manager.run_direkt(
            #~ "pygmentsize", "write_sourcecode", ext, code, out_object
        #~ )

        from PyLucid.buildin_plugins.pygmentsize import pygmentsize

        p = pygmentsize.pygmentsize(self.request, self.response)

        if out_object != None:
            # tinyTextile gibt ein out-Objekt vor.
            out_object.write(p.get_sourcecode(ext, code, pygments_style))
        else:
            # direkt in response schreiben
            p.write_sourcecode(ext, code, pygments_style)





