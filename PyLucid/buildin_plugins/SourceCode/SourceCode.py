#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"



import sys, os, cgi, sys



from PyLucid.system.BaseModule import PyLucidBaseModule

class SourceCode(PyLucidBaseModule):

    def lucidFunction( self, function_info ):
        filepath = function_info # Daten aus dem <lucidFunction>-Tag
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
            test_path = "%s%s" % (os.environ["DOCUMENT_ROOT"], filepath)
            if os.path.isfile(test_path):
                filepath = test_path
            else:
                test_path = os.path.join(
                    os.environ["DOCUMENT_ROOT"], filepath
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
        ext = ext[1:] # .py -> py

        self.render.highlight(ext, source.strip())

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












