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

__version__="0.2.0"

__history__="""
v0.2.0
    - Anpassung damit es mit lucidFunction funktioniert.
v0.1.1
    - Bug in Python-Highlighter: Zeilen mit einem "and /" am Ende wurden falsch dagestellt.
v0.1.0
    - erste Version
"""


import cgitb;cgitb.enable()
import sys, os, cgi

# Imports für Parser()
import string, cStringIO, keyword, token, tokenize



#_______________________________________________________________________
# Module-Manager Daten


class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "SourceCode" : {
            "lucidFunction" : "SourceCode", # <lucidFunction:SourceCode>'Dateiname'</lucidFunction>
            "must_login"    : False,
            "must_admin"    : False,
        },
    }



#_______________________________________________________________________



_KEYWORD = token.NT_OFFSET + 1



class Parser:
    """
    Diese Klasse basiert auf Jürgen Hermann's "MoinMoin - Python Source Parser"
    siehe: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298/
    """

    def __init__( self, raw ):
        """ Store the source text.
        """
        self.raw = string.strip(string.expandtabs(raw))

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
            print "<h3>ERROR: %s</h3>%s\n" % (
                msg, self.raw[self.lines[line]:]
            )

        print "<br/>"


    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler.
        """
        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        # handle newlines
        if toktype in (token.NEWLINE, tokenize.NL):
            print '<br\>\n'
            return

        # Spaces
        if newpos > oldpos:
            print self.raw[oldpos:newpos].replace(" ","&nbsp;")

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

        print '<span class="t%s">%s</span>' % (toktype,toktext)

        #~ print "\n>>>",toktype



#~ Parser( open(__file__).read() ).parse()
#~ sys.exit()






class source_code:

    def get_file( self, filename ):
        filepath = os.environ["DOCUMENT_ROOT"] + filename
        filepath = os.path.normpath( filepath )

        try:
            f = file( filepath, "rU" )
            source = f.read()
            f.close()
        except Exception, e:
            print "Error to Display file '%s' (%s)" % ( filename, e )
            return

        print '<div class="SourceCodeFilename">%s</div>' % filename

        if os.path.splitext( filename )[1] == ".py":
            self.print_CSS()
            print '<div class="SourceCode">'
            Parser( source ).parse()
        else:
            print '<div class="SourceCode">'
            self.format_code( source )

        print '</div>'

    def print_CSS( self ):
        print '<style type="text/css">\n'
        print ".t%s { color: #0080C0; }\n" % token.NUMBER
        print ".t%s { color: #0000C0; }\n" % token.OP
        print ".t%s { color: #004080; }\n" % token.STRING
        print ".t%s { color: #008000; }\n" % tokenize.COMMENT
        print ".t%s { color: #000000; }\n" % token.NAME
        print ".t%s { color: #FF8080; }\n" % token.ERRORTOKEN
        print ".t%s { color: #C00000; }\n" % _KEYWORD
        print "</style>\n"

    def format_code( self, source ):
        for line in source.split("\n"):
            line = cgi.escape( line )
            line = line.replace("\t","    ") # Tabulatoren nach Leerzeilen
            line = line.replace(" ","&nbsp;") # Leerzeilen nach non-breaking-Spaces
            print line, "<br/>"

    def getCGIdata( self ):
        "CGI-POST Daten auswerten"
        data = {}
        FieldStorageData = cgi.FieldStorage( keep_blank_values=True )
        for i in FieldStorageData.keys(): data[i] = FieldStorageData.getvalue(i)
        return data


def PyLucid_action( PyLucid, function_string ):
    # Aktion starten
    source_code().get_file( function_string )

