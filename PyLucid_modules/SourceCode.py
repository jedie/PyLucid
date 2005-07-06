#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
SourceCode.py - Source Code - CGI
(GPL-License)
by JensDiemer.de

Zeigt auf dem Webserver eine Source-Datei an.
Python-Code wird mit einem Parser gehighlighted.

Anmerkung:
----------
Eigentlich könnte man prima mit CSS's "white-space:pre;" arbeiten und
somit alle zusätzlichen " " -> "&nbsp;" und "\n" -> "<br/>" umwandlung
sparen. Das Klappt aus mit allen Browsern super, nur nicht mit dem IE ;(

http://jensdiemer.de/?lucid_SourceCode
"""

__version__="0.1.1"

__history__="""
v0.1.1
    - Bug in Python-Highlighter: Zeilen mit einem "and /" am Ende wurden falsch dagestellt.
v0.1.0
    - erste Version
"""


import cgitb;cgitb.enable()
print "Content-type: text/html\n"

import sys, os, cgi

# Imports für Parser()
import string, cStringIO, keyword, token, tokenize


_KEYWORD = token.NT_OFFSET + 1

CSS  = '<style type="text/css">\n'
CSS += '.code { font-family:"Courier New",Courier,monospace; }\n'
CSS += ".t%s { color: #0080C0; }\n" % token.NUMBER
CSS += ".t%s { color: #0000C0; }\n" % token.OP
CSS += ".t%s { color: #004080; }\n" % token.STRING
CSS += ".t%s { color: #008000; }\n" % tokenize.COMMENT
CSS += ".t%s { color: #000000; }\n" % token.NAME
CSS += ".t%s { color: #FF8080; }\n" % token.ERRORTOKEN
CSS += ".t%s { color: #C00000; }\n" % _KEYWORD
CSS += "</style>\n"

class Parser:
    """
    Diese Klasse basiert auf Jürgen Hermann's "MoinMoin - Python Source Parser"
    siehe: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298/
    """

    def __init__(self, raw, out = sys.stdout):
        """ Store the source text.
        """
        self.raw = string.strip(string.expandtabs(raw))
        self.out = out

    def parse( self ):
        " Parse and send the colored source. "

        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = string.find( self.raw, '\n', pos ) + 1
            if not pos: break
            self.lines.append( pos )
        self.lines.append( len(self.raw) )

        # parse the source and write it
        self.pos = 0
        text = cStringIO.StringIO( self.raw )

        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            self.out.write("<h3>ERROR: %s</h3>%s\n" % (
                msg, self.raw[self.lines[line]:]))

        self.out.write("<br/>")


    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler.
        """
        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        # handle newlines
        if toktype in (token.NEWLINE, tokenize.NL):
            self.out.write('<br\>\n')
            return

        # Spaces
        if newpos > oldpos:
            self.out.write( self.raw[oldpos:newpos].replace(" ","&nbsp;") )

        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = _KEYWORD

        # Text Escapen
        toktext = cgi.escape( toktext )

        # Zeilenumbrüche umwandeln
        toktext = toktext.replace("\n","<br\>\n")

        # Non-Breaking-Spaces
        toktext = toktext.replace(" ","&nbsp;")

        self.out.write(
            '<span class="t%s">%s</span>' % (toktype,toktext)
        )

        #~ print "\n>>>",toktype



#~ Parser( open(__file__).read() ).parse()
#~ sys.exit()




class coder:
    def __init__( self ):
        if os.environ["REMOTE_ADDR"] != os.environ["SERVER_ADDR"]:
            # Aufruf nur vom Server selber aus erlaubt.
            # Also von lucid's IncludeRemote aus!
            self.error(
                "not allowed! %s - %s" % (
                    os.environ["REMOTE_ADDR"], os.environ["SERVER_ADDR"]
                )
            )

        cgidata = self.getCGIdata()

        if not cgidata.has_key("file"):
            self.error( "no file parameter" )

        filename = cgidata["file"]
        filename = os.environ["DOCUMENT_ROOT"] + filename
        if not os.path.isfile( filename ):
            self.error( "File '%s' not found!" % filename )

        name, ext = os.path.splitext( filename )

        if ext == ".py":
            print CSS
            print '<div class="code">'
            self.MoinMoinSourceParser( filename )
            print '</div>'
        else:
            print '<div class="code">'
            self.printcode( filename )
            print '</div>'

    def printcode( self, filename ):
        f = file( filename, "rU" )
        for line in f:
            line = cgi.escape( line )
            line = line.replace("\t","    ") # Tabulatoren nach Leerzeilen
            line = line.replace(" ","&nbsp;") # Leerzeilen nach non-breaking-Spaces
            print line + "<br/>"

        f.close()

    def MoinMoinSourceParser( self, filename ):
        f = file( filename, "rU" )
        source = f.read()
        f.close()

        Parser( source ).parse()

    def error( self, txt ):
        print txt
        sys.exit()

    def getCGIdata( self ):
        "CGI-POST Daten auswerten"
        data = {}
        FieldStorageData = cgi.FieldStorage( keep_blank_values=True )
        for i in FieldStorageData.keys(): data[i] = FieldStorageData.getvalue(i)
        return data

if __name__ == "__main__":
    coder()