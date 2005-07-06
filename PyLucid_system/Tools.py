#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__="0.0.1"

"""
Routinen die von mehreren Modulen benutzt werden werden hier zusammengefasst
"""

# Das Modul wird gar nicht mehr verwendet:
raise


import sys, xml.sax.saxutils, re

def error( txt ):
    print "Content-type: text/html\n"
    print "<h1>Error!</h1>"
    print "<h2>%s</h2>" % xml.sax.saxutils.escape( txt )
    sys.exit(1)

#~ print ">>> Lokaler Test!!!"
#~ error("Nur ein lokaler Test!")


TestTemplate = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>TEST</title>
<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />
<meta name="MSSmartTagsPreventParsing" content="TRUE" />
<meta http-equiv="imagetoolbar"        content="no" />
<style>
* {
    /* uebergreifende Schriftart */
    font-family: tahoma, arial, sans-serif;
    color: #000000;
}
body {
	font-size: 0.9em;
	background-color: #678FAD;
}
.Gallery ul {
	text-align: center;
	margin: 0px;
	padding: 0px;
}
.Gallery li {
	float: left;
	border: 1px solid #EAECFF;
	height: 150px;
	width: auto;
	text-align: center;
	margin: 5px;
	padding: 5px;
	list-style-type: none;
	background-color: #EDF1FF;
}
.clear {
	clear: both;
	margin: 5px;
	padding: 5px;
	border: none;
}
</style>
</head>
<body>
<h2>TEST</h2>
<ul class="Gallery">
<!-- StartLoop -->
<li>
    <p>%(CleanFilename)s</p>
    <p><a href="%(PreviewFile)s" title="Klicken f&uuml;r kleine Preview">
        <img src="%(ThumbFile)s" border="0" alt="" />
    </a></p>
    <p><a href="%(SourceFile)s" title="Download mit rechter Maustaste: 'Speichern unter...'">
        Druck-Version download - %(FileSize)s
    </a></p>
</li>
<!-- EndLoop -->
</ul>
<hr class="clear" />
</body>
</html>
"""
class LoopTemplate:
    def __init__( self, template ):
        self.start_tag = "<!-- StartLoop -->"
        self.end_tag = "<!-- EndLoop -->"

        self.template = template
        self.parse()

    def parse( self ):
        self.start_tag  = re.escape( self.start_tag )
        self.end_tag    = re.escape( self.end_tag )
        template = re.findall( "(.*?)" + self.start_tag + "(.*?)" + self.end_tag + "(.*?)", self.template )
        print "(.*?)" + self.start_tag + "(.*?)" + self.end_tag + "(.*?)"
        print self.template
        print template

MyLT = LoopTemplate( TestTemplate )
#~ MyLT.debug()
sys.exit()

class LoopTemplate:
    def __init__( self, template ):
        self.template = template
        self.elements = {}
        self.element_escape = "~~"

    def parse( self ):
        self.extract()

    def extract( self ):
        areas = [
                ( "<!-- StartLoop -->", "<!-- EndLoop -->" )
            ]
        for area in areas:
            element_id = len(self.elements)
            element_mark = "%(esc)s%(id)s%(esc)s" % {
                "esc"   : self.element_escape,
                "id"    : element_id
                }
            print element_mark, area
            #~ try:
            reString = re.escape(area[0])+"(.*?)"+re.escape(area[1])
            print reString
            regex = re.compile( reString, re.I | re.S | re.M )
            result = regex.search( self.template )
            print result.group()
            print area[2], result.group(1)
            self.elements[element_id] = ( area[2], result.group(1) )
            self.elements = self.template.replace(result.group(0), element_mark, 1)
            #~ except:
                #~ pass

    def debug( self ):
        print self.elements

MyLT = LoopTemplate( TestTemplate )
MyLT.parse()
MyLT.debug()

#~ if __name__ == "__main__":
    #~ print ">>> Lokaler Test!!!"
    #~ error("Nur ein lokaler Test!")






