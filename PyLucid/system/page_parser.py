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

from PyLucid.tools.out_buffer import out_buffer



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
                out = out_buffer(self.page_msg)
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
                #~ except Exception, e:
                    #~ msg = "Can't use textile-Markup (%s)" % e
                    #~ self.page_msg(msg)
                    #~ return msg
            else:
                from PyLucid.system import tinyTextile
                out = out_buffer(self.page_msg)
                t = tinyTextile.parser(out, self.request, self.response)
                t.parse(content)
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg("Markup '%s' not supported yet :(" % markup)
            return content

    #_________________________________________________________________________

    def highlight(self, ext, code, out_object=None):
        """
        Schnittstelle zu pygments

        zu benutzten i.d.R.:

        self.render.highlight(ext, sourcecode)

            ext..: Typische Dateiendung (Bsp.: py, .py, css, html)
            code.: der Sourcecode als String
        """
        ext = ext.lower().lstrip(".")
        if out_object == None:
            out_object = self.response

        html_fieldset = (
            '<fieldset class="syntax"><legend class="syntax">%s</legend>\n',
            '</fieldset><br />'
        )

        ## Für das automatische Generieren des Styles
        ## Die Daten kommen aus PyKleur und werden in die Seite
        ## eingeblendet. Dann kann man das ganze per Copy&Paste in's
        ## PyLucid Style einbauen
        #~ from pygments.formatters import HtmlFormatter
        #~ from pygments.styles import get_style_by_name
        #~ css_style = HtmlFormatter(style='friendly').get_style_defs('.syntax')
        #~ self.response.write("<pre>")
        #~ self.response.write(css_style)
        #~ self.response.write("</pre>")


        def fallback_write(code, legend_info):
            out_object.write(html_fieldset[0] % legend_info)
            out_object.write("<pre>")
            out_object.write(code)
            out_object.write("</pre>")
            out_object.write(html_fieldset[1])

        #~ fallback_write(code, "DEBUG!!")
        #~ return

        try:
            #~ raise ImportError("TEST")
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter
            from pygments import highlight
        except ImportError, e:
            legend_info = "%s [Pygments ImportError: %s]" % (ext, e)
            fallback_write(code, legend_info)
            return


        try:
            #~ raise Exception("TEST")
            lexer = get_lexer_by_name(ext)
        except ValueError:
            # pykleur.lexers.get_lexer_by_name schmeist den ValueError
            # -> Kein Lexer für das Format vorhanden
            lexer = get_lexer_by_name("text")
            legend_info = (
                "%s <small>(unknown format, use TextLexer)</small>"
            ) % ext
            out_object.write(html_fieldset[0] % legend_info)
        except Exception, e:
            legend_info = "%s [Pygments get_lexer error: %s]" % (ext, e)
            fallback_write(code, legend_info)
            return
        else:
            out_object.write(html_fieldset[0] % lexer.name)

        try:
            #~ raise Exception("TEST")
            formatter = HtmlFormatter(
                linenos=True, encoding="utf-8"
            )
            highlight(code, lexer, formatter, out_object)
        except Exception, e:
            self.page_msg("Pygments HtmlFormatter Error: %s" % e)
            out_object.write("<pre>%s</pre>\n" % code)

        out_object.write(html_fieldset[1])
