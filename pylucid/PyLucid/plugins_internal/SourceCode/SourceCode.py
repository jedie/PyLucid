# -*- coding: utf-8 -*-

"""
Zeigt auf dem Webserver eine Source-Datei an.
Python-Code wird mit einem Parser gehighlighted.

Anmerkung:
----------
Eigentlich könnte man prima mit CSS's "white-space:pre;" arbeiten und
somit alle zusätzlichen " " -> "&nbsp;" und "\n" -> "<br/>" umwandlung
sparen. Das Klappt aus mit allen Browsern super, nur nicht mit dem IE ;(


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



import sys, os, cgi, sys

from PyLucid.system import hightlighter

from PyLucid.system.BasePlugin import PyLucidBasePlugin

class SourceCode(PyLucidBasePlugin):

    def lucidTag(self, url):
        filepath = url
        try:
            filename = os.path.split(filepath)[1]
        except Exception, e:
            msg = (
                "SourcCode Plugin Error:"
                " wrong path '%s'! (%s)"
            ) % (cgi.escape(repr(function_info)), cgi.escape(e.args[0]))
            self.page_msg.red(msg)
            return

        if not os.path.isfile(filepath):
            test_path = "%s%s" % (
                os.environ.get("DOCUMENT_ROOT", ""), filepath
            )
            if os.path.isfile(test_path):
                filepath = test_path
            else:
                test_path = os.path.join(
                    os.environ.get("DOCUMENT_ROOT", ""), filepath
                )
                if os.path.isfile(test_path):
                    filepath = test_path
                else:
                    self.page_msg(
                        "SourceCode Error: File '%s' not found!" % filepath
                    )
                    return

        try:
            f = file( filepath, "rU" )
            source = f.read()
            f.close()
        except Exception, e:
            self.page_msg(
                "SourceCode Error: Can't open file '%s' (%s)" % (filename, e)
            )
            return

        ext = os.path.splitext(filename)[1] # blabla.py -> .py

        try:
            html = hightlighter.make_html(source.strip(), ext)
            self.response.write(html)
            return
        except Exception, e:
            self.page_msg("Error: %s" % e)

        self.format_code(source)

    def format_code( self, source ):
        """
        Source-Code außer Python-Source anzeigen
        """
        for line in source.split("\n"):
            line = cgi.escape(line)
            line = line.replace("\t","    ") # Tabulatoren nach Leerzeilen
            self.response.write("%s\n" % line)

    #~ def download(self, file):
        #~ print "Location: %s\n" % file
        #~ print "Content-type: text/plain\n";
        #~ sys.exit()












