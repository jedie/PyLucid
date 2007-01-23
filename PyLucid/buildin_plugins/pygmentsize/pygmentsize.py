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


#~ debug = True
debug = False


from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight

from PyLucid.tools.OutBuffer import OutBuffer
from PyLucid.system.BaseModule import PyLucidBaseModule


class pygmentsize(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(pygmentsize, self).__init__(*args, **kwargs)

        self.current_pygments_style = "default" #self.plugin_cfg["default_style"]

        #~ if debug: self.page_msg("style:", self.current_pygments_style)

    def setup(self):
        raise NotImplemented

    #_________________________________________________________________________

    def write_sourcecode(self, ext, sourcecode, pygments_style=None):
        """
        Hightlighted the sourcecode and write it directly into the
        global response object
        """
        context = self._get_context(ext, sourcecode, pygments_style)

        self.templates.write("sourcecode_block", context, debug=False)

    def get_sourcecode(self, ext, sourcecode, pygments_style=None):
        """
        returns the hightlighted sourcecode
        """
        context = self._get_context(ext, sourcecode, pygments_style)

        return self.templates.get_rendered_page("sourcecode_block", context)

    #_________________________________________________________________________

    def _get_context(self, ext, sourcecode, pygments_style):
        """
        Liefert den Context zum rendern der internen-Seite zurück.
            - Schreibt die CSS Daten
            - Holt sich den passenden Lexter anhand der Dateiendung
            - Highlightet den Sourcecode
            - baut das context dict zusammen
        """
        try:
            current_style = self.write_style(pygments_style)

            lexer, lexer_name = self.get_lexer_by_ext(ext)
            sourcecode = self.get_highlighted(lexer, sourcecode)
        except PygmentsError, e:
            self.response.write("<p>[Pygments Error: %s]</p>" % e)
            context = {
                "lexer_name": ext,
                "sourcecode": sourcecode,
                "current_style": "[None]",
            }
        else:
            context = {
                "lexer_name": lexer_name,
                "sourcecode": sourcecode,
                "current_style": current_style,
            }

        return context

    #_________________________________________________________________________

    def write_style(self, pygments_style):
        """
        Schreibt den pygments style per self.templates.add_CSS, aber nur einmal
        """
        if hasattr(self.response, "pygments_style_written"):
            # Der Style wurde schon einmal ausgegeben
            if debug: self.page_msg("Pygments style already written.")
            return
        else:
            if debug: self.page_msg("send new pygments style.")
            self.response.pygments_style_written = True

        if pygments_style == None:
            pygments_style = self.current_pygments_style

        stylesheet, current_style = self.get_style(pygments_style)
        self.templates.add_CSS(stylesheet, "pygmentsize")
        return current_style

    def get_style(self, current_style):
        if current_style == None:
            current_style = "default"

        try:
            formatter = HtmlFormatter(style=current_style)
        except ValueError, e:
            # Style nicht da?
            formatter = HtmlFormatter()
            current_style = "[get Style Error: %s - Use default.]" % e
        except Exception, e:
            raise PygmentsError("Can't get formatter (get_style): %s" % e)

        try:
            stylesheet = formatter.get_style_defs('.pygments_code')
        except Exception, e:
            raise PygmentsError("Can't get stylesheet from formatter: %s" % e)

        return stylesheet, current_style

    #_________________________________________________________________________

    def get_lexer_by_ext(self, ext):
        """
        Liefert lexer-Objekt und Namen anhand der Datei-Endung zurück
        """
        ext = ext.lower().lstrip(".")

        try:
            lexer = get_lexer_by_name(ext)
        except ValueError:
            # pykleur.lexers.get_lexer_by_name schmeist den ValueError
            # -> Kein Lexer für das Format vorhanden
            lexer = get_lexer_by_name("text")
            return lexer, "[unknown format, use TextLexer]"
        except Exception, e:
            raise PygmentsError("Can't get lexer: %s" % e)
        else:
            return lexer, lexer.name

    def get_highlighted(self, lexer, sourcecode):
        """
        Liefert den highlighted sourcecode zurück
        """
        out_object = OutBuffer(self.page_msg)

        try:
            formatter = HtmlFormatter(linenos=True, encoding="utf-8")
        except Exception, e:
            out_object.get() # Reset!
            raise PygmentsError("Can't get formatter: %s" % e)

        try:
            highlight(sourcecode, lexer, formatter, out_object)
        except Exception, e:
            out_object.get() # Reset!
            raise PygmentsError("Can't highlight: %s" % e)

        return out_object.get()


class PygmentsError(Exception):
    pass
class NoLexerAvailable(PygmentsError):
    pass