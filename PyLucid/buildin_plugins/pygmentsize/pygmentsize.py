#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""A small Layer to pygments

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

__version__= "$Rev$"


from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight

from PyLucid.tools.OutBuffer import OutBuffer
from PyLucid.system.BaseModule import PyLucidBaseModule


class pygmentsize(PyLucidBaseModule):

    def setup(self):
        raise NotImplemented

    #_________________________________________________________________________

    def write_sourcecode(self, ext, sourcecode, pygments_style=None):
        """
        Hightlightet den Sourcecode und schreibt ihn direkt in das
        globale response Objekt
        """
        context = self._get_context(ext, sourcecode)
        #~ self.page_msg(context)

        current_style = self.write_style(pygments_style)
        context["current_style"] = current_style

        self.templates.write("sourcecode_block", context, debug=False)

    def get_sourcecode(self, ext, sourcecode, write_css=True,
                                                        pygments_style=None):
        """
        Liefert die gerendetere Interne Seite zurück
        (Wird von tinyTextile verwendet)
        """
        context = self._get_context(ext, sourcecode)
        context["current_style"] = "[None]"
        return self.templates.get_rendered_page("sourcecode_block", context)

    #_________________________________________________________________________

    def _get_context(self, ext, sourcecode):
        """
        Liefert den Context zum rendern der internen-Seite zurück.
            - Holt sich den passenden Lexter anhand der Dateiendung
            - Highlightet den Sourcecode
            - baut das context dict zusammen
        """
        lexer, lexer_name = self.get_lexer_by_ext(ext)

        sourcecode = self.get_highlighted(lexer, sourcecode)

        context = {
            "lexer_name": lexer_name,
            "sourcecode": sourcecode,
        }
        return context

    #_________________________________________________________________________

    def write_style(self, pygments_style):
        stylesheet, current_style = self.get_style(pygments_style)
        self.templates.addCSS(stylesheet, "pygmentsize")
        return current_style

    def get_style(self, current_style):
        if current_style == None:
            current_style = "default"

        try:
            formatter = HtmlFormatter(style=current_style)
        except ValueError, e:
            # Style nicht da?
            formatter = HtmlFormatter()
            current_style = "[Error: %s]" % e

        stylesheet = formatter.get_style_defs('.pygments_code')

        return stylesheet, current_style

    #_________________________________________________________________________

    def get_lexer_by_ext(self, ext):
        """
        Liefert lexer-Objekt und Namen anhand der Datei-Endung zurück
        """
        ext = ext.lower().lstrip(".")

        try:
            #~ raise Exception("TEST")
            lexer = get_lexer_by_name(ext)
        except ValueError:
            # pykleur.lexers.get_lexer_by_name schmeist den ValueError
            # -> Kein Lexer für das Format vorhanden
            lexer = get_lexer_by_name("text")
            return lexer, "[unknown format, use TextLexer]"
        else:
            return lexer, lexer.name

    def get_highlighted(self, lexer, sourcecode):
        """
        Liefert den highlighted sourcecode zurück
        """
        out_object = OutBuffer(self.page_msg)

        formatter = HtmlFormatter(
            linenos=True, encoding="utf-8"
        )
        highlight(sourcecode, lexer, formatter, out_object)

        return out_object.get()


class PygmentsError(Exception):
    pass
class NoLexerAvailable(PygmentsError):
    pass