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
"""

__version__="0.4"

__history__="""
v0.4
    - Nutzt nun PyKleur, durch self.render.highlight()
v0.3.1
    - Nutzt <pre>
v0.3
    - Anpassung an PyLucid v0.7
v0.2.6
    - Anpassung an änderung im SourceCode-Parser
v0.2.5
    - Anpassung an neuen ModuleManager
v0.2.4
    - lucidFunction() erwartet nun auch function_info vom ModulManager
v0.2.3
    - Python Source Code Parser ausgelagert nach sourcecode_parser.py, damit
        er auch mit tinyTextile genutzt werden kann
v0.2.2
    - Falscher <br>-Tag korrigiert
v0.2.1
    - zwei print durch sys.stdout.write() ersetzt, da ansonsten ein \n
        eingefügt wurde, der im Browser eine zusätzliches Leerzeichen
        produzierte und somit den Source-Code unbrauchbar machte :(
v0.2.0
    - Anpassung damit es mit lucidFunction funktioniert.
v0.1.1
    - Bug in Python-Highlighter: Zeilen mit einem "and /" am Ende wurden
        falsch dagestellt.
v0.1.0
    - erste Version
"""


import sys, os, cgi, sys



from PyLucid.system.BaseModule import PyLucidBaseModule

class SourceCode(PyLucidBaseModule):

    def lucidFunction( self, function_info ):
        filepath = function_info # Daten aus dem <lucidFunction>-Tag
        filename = os.path.split(filepath)[1]

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












