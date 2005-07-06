#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
CGI-DEMO von TinyTextile

(GPL-License)
by jensdiemer.de

http://jensdiemer.de/index.php?TinyTextile
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1.1"

__history__="""
v0.1.1
    - Als Starttext wird tinyTextile.syntax_help genommen
v0.1.0
    - erste Version
"""

__todo__ = """
"""

import cgitb;cgitb.enable()
print "Content-type: text/html\n"

import sys, os, cgi, xml.sax.saxutils

import tinyTextile






HelpFileHead = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>tinyTextile - Helpfile</title>
<meta name="Author"                    content="Jens Diemer" />
<meta http-equiv="content-language"    content="de" />
<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />
<meta name="MSSmartTagsPreventParsing" content="TRUE" />
<meta http-equiv="imagetoolbar"        content="no" />
</head>
<body>
"""
HelpFileFoot = """</body></html>"""













class demo:
    def __init__( self ):
        cgidata = self.getCGIdata()
        #~ self.cgidata = cgidata

        if cgidata.has_key("content") and (not cgidata.has_key("reset")):
            txt = cgidata["content"]
        else:
            txt = tinyTextile.syntax_help

        self.print_html( txt )

    def getCGIdata( self ):
        "CGI-POST Daten auswerten"
        data = {}
        FieldStorageData = cgi.FieldStorage( keep_blank_values=True )
        for i in FieldStorageData.keys(): data[i] = FieldStorageData.getvalue(i)
        return data

    def print_html( self, txt ):
        HomeLink = '<a href="http://www.jensdiemer.de/?TinyTextile">&lt; zurück zur Homepage</a>'

        print '<?xml version="1.0" encoding="UTF-8"?>'
        print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">'
        print '<html xmlns="http://www.w3.org/1999/xhtml">'
        print '<head>'
        print '<title>tinyTextile - CGI-DEMO</title>'
        print '<meta name="Author"                    content="Jens Diemer" />'
        print '<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />'
        print '</head><body>'
        print '<h3>tinyTextile - CGI-DEMO</h3>'
        print HomeLink

        print '<form name="data" method="post" action=""><p>'
        print '<textarea name="content" cols="100" rows="25" wrap="VIRTUAL">'
        print xml.sax.saxutils.escape(txt)
        print '</textarea><br/>'
        print '<input type="submit" name="Submit" value="Submit" />'
        print '<input type="submit" name="reset" value="reset to Syntax-HelpText" />'
        print '</p></form>'
        #~ print xml.sax.saxutils.escape( str(self.cgidata) )
        print "<h3>Erzeugte HTML-Seite:</h3>"
        print '<hr>'

        tinyTextile.parser( sys.stdout ).parse( txt )
        #~ tinyTextile.parser( sys.stdout, newline="" ).parse( txt )

        print '<hr>'
        print HomeLink
        print '</body></html>'


if __name__ == "__main__":
    demo()



