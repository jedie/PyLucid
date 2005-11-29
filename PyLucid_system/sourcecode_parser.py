#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Source Code Parser

Based on Jürgen Hermann's "MoinMoin - Python Source Parser"
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298/
"""

__version__="0.2.0"

__history__="""
v0.2.0
    - Einige Optimierungen
    - Bug mit den speziellen ZeilenumbrÃ¼che mit \ am ende (kein Zeilenumbruch) behoben
v0.1.0
    - aus SourceCode.py Plugin entnommen, damit er auch für tinyTextile genutzt werden kann
"""

import sys, cgi, cStringIO, \
    keyword, token, tokenize

token.KEYWORD = token.NT_OFFSET + 1

class python_source_parser:

    def parse( self, raw_txt ):
        """
        Parse and send the colored source.
        """
        self.special_not_newline = False
        self.raw = raw_txt.expandtabs()

        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find( '\n', pos ) + 1
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

        print "<br />\n"


    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler.
        """
        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        # Patch for special not newline with \
        if line.endswith("\\\n") and toktype!=tokenize.COMMENT:
            self.special_not_newline = True
        elif self.special_not_newline == True:
            self.special_not_newline = False
            print "\\<br />\n"

        # handle newlines
        if toktype in (token.NEWLINE, tokenize.NL):
            sys.stdout.write( '<br />\n' )
            return

        # Spaces
        if newpos > oldpos:
            sys.stdout.write("&nbsp;" * (newpos-oldpos))

        if toktext=="":
            return

        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = token.KEYWORD

        # Text Escapen
        toktext = cgi.escape( toktext )

        # Non-Breaking-Spaces
        toktext = toktext.replace(" ","&nbsp;")

        # ZeilenumbrÃ¼che umwandeln
        toktext = toktext.replace("\n","<br />\n")

        if toktype==token.NAME:
            sys.stdout.write(toktext)
        else:
            sys.stdout.write('<span class="t%s">%s</span>' % (toktype,toktext))

        #~ print "\n>>>",toktype

    def get_CSS( self ):
        CSS  = '<style type="text/css">\n'
        CSS += ".t%s { color: #0080C0; }\n" % token.NUMBER
        CSS += ".t%s { color: #0000C0; }\n" % token.OP
        CSS += ".t%s { color: #004080; }\n" % token.STRING
        CSS += ".t%s { color: #008000; }\n" % tokenize.COMMENT
        CSS += ".t%s { color: #000000; }\n" % token.NAME
        CSS += ".t%s { color: #FF8080; }\n" % token.ERRORTOKEN
        CSS += ".t%s { color: #C00000; }\n" % token.KEYWORD
        CSS += "</style>\n"
        return CSS


if __name__ == '__main__':
    import re
    import tools

    clean_re1=re.compile(r'\<span class=".*?"\>')
    clean_re2=re.compile(r'\</span\>')

    def print_clean(txt):
        txt = txt.encode("String_Escape")
        txt = txt.replace("&nbsp;"," ")
        txt = txt.replace("<br />","\n")
        txt = clean_re1.sub(r"", txt)
        txt = clean_re2.sub(r"", txt)
        print txt

    redirector = tools.redirector()
    python_source_parser().parse(open(__file__).read())
    print_clean(redirector.get())

    #~ python_source_parser().parse( open(__file__).read() )
