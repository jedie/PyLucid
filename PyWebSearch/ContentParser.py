#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Extrahiert den Text aus HTML-Seiten.
"""

__version__="0.0.1"



import sys, re, sgmllib




class MetaContentParser(sgmllib.SGMLParser):

    """
    Extrahiert den Text aus HTML-Seiten.
    Unterscheidet die folgende Daten:
        - title
        - meta-Tags-Informationen
        - Überschriften
        - nomaler Text
    """

    entitydefs = {
        "nbsp" : " ",
        "Auml" : "Ä",
        "auml" : "ä",
        "Ouml" : "Ö",
        "ouml" : "ö",
        "Uuml" : "Ü",
        "uuml" : "ü"
        }

    def __init__(self):
        # MetaTags die berücksichtigt werden sollen.
        self.metaTags = ["keywords","description","author"]

        sgmllib.SGMLParser.__init__(self, 0)

        self.data = {
            "title"     : " ",
            "meta"      : " ",
            "heads"     : " ",
            "content"   : " "
        }
        self.typ = "content"

    ###
    ### Default Funktionen
    ###

    def start_title( self, dummy ):
        self.typ = "title"

    def end_title( self ):
        self.typ = "content"

    def start_meta( self, metaData ):
        try:
            typ = metaData[0][1]
            content = metaData[1][1]
        except:
            return

        if not typ.lower() in self.metaTags:
            return

        content = " ".join( content.split(",") )
        self.data["meta"] += " " + content

    def handle_data( self, data ):
        try:
            self.data[self.typ] += data
        except UnicodeError:
            pass

    #~ def feed(self, data):
        #~ "Original Version überschreiben"
        #~ try:
            #~ self.rawdata = self.rawdata + data
        #~ except UnicodeError:
            #~ pass
        #~ self.goahead(0)

    def unknown_starttag(self, tag, attrs):
        if tag[0] == "h":
            # Überschriften
            self.typ = "heads"
        else:
            self.typ = "content"

    def cleancontent( self ):
        "Leerzeichen verwerfen, nur Buchstaben zulassen"
        for typ in self.data:
            self.data[typ] = " ".join(
                    re.findall( r"[\wäöüßÄÖÜ]+",self.data[typ] )
                )

    ###
    ### Abfragen der Daten
    ###

    def get_data( self ):
        self.cleancontent()
        return self.data

    def dump( self ):
        for k,v in self.get_data().iteritems():
            print ">",k
            print v
            print "-"*80
        #~ print self.get_data()



TestTXT ="""<!DOCTYPE html
     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<!-- InstanceBegin template="/Templates/XHTML.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<!-- Copyright (c) 2004 Jens Diemer -->
<!-- #BeginEditable "doctitle" -->
<title>Jens m&ouml;gliche &uuml;ber  Diemer</title>
<!-- #EndEditable --><!-- InstanceBeginEditable name="head" -->
<meta name="Keywords" content="Jens,Diemer,Diplom,Designer,3D,Video,Grafik,Homepage,Design,Effekte,Animation,Animationen,NRW,Rhein-Ruhr,Duisburg" />
<meta name="Description" content="Dies ist die private Homepage von Jens Diemer.
Hier gibt es alles m&ouml;gliche &uuml;ber mich und mein Studium an der FH-D&uuml;sseldorf..." />
<!-- InstanceEndEditable -->
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<meta http-equiv="content-language" content="de" />
<meta name="Description" content="Jens Diemer Homepage" />
<meta name="Author" content="Jens Diemer" />
<meta name="Copyright" content="(c) 1997-2004 Jens Diemer" />

<meta name="MSSmartTagsPreventParsing" content="TRUE" />
<meta http-equiv="imagetoolbar" content="no" />
<script src="css/css.js" type="text/javascript"></script>
<noscript>
<link href="css/XHTML_Web_Blau.css" rel="stylesheet" title="Blau" type="text/css" />
</noscript>
<!-- InstanceBeginEditable name="SeitenStyles" -->
<style type="text/css">
<!--
.BrowserInfo2 {
	border: 1px solid #000000;
}
.backUnten2 {
	display:none;
}
-->
</style>
<!-- InstanceEndEditable -->
</head><body onload="start();" onunload="ende();">m&ouml;gliche &uuml;ber
<div id="Seite">
  <h1><!-- InstanceBeginEditable name="SeitenName" --><span class="Titel">Jens Diemer</span><!-- InstanceEndEditable --></h1>
  <div class="backOben"><!-- InstanceBeginEditable name="backOben" --><!-- InstanceEndEditable --></div>

  <!-- InstanceBeginEditable name="SeitenInfo" -->
<div class="SeitenInfo">
  <noscript class="noscriptInfo"><p>Bitte schalten Sie JavaScript ein!</p></noscript>
  <h3>Was es Neues gibt:</h3>
  <ul>
    <li>- 21.04.2005 - Ein Blick auf meine neue Webseite:<a href="http://cms.jensdiemer.de">CMS</a></li>
    <li>- 28.02.2005 - Fritz Cizmarov aka <a href="http://python.sandtner.org/viewtopic.php?t=2867">Dookie</a> verstarb völlig unerwartet an einem Grippe-Virus</li>

    <li>- 23.02.2005 - <a href="Programmieren/PyDiskEraser/index.html">PyDiskEraser</a> ein neues kleines Python-Skript</li>
    <li>- 21.01.2005 - <a href="Video/Plus/index.html">PLUS</a> ist nun in der neuen Release 2c zum Download verf&uuml;gbar! </li>
    </ul>
</div>
<!-- InstanceEndEditable -->

  <div class="Block"> <!-- InstanceBeginEditable name="TextBlock" -->
  <h2>Studium FH-D&uuml;sseldorf</h2>
  <ul>
    <li><a href="Video/index.html">Video's</a></li>
    <li><a href="Kurse/index.html">Arbeiten aus Kursen</a></li>
    <li><a href="KursPlan/index.htm">&Uuml;bersicht &uuml;ber meine Kurse</a></li>

  </ul>
  <h2>Pers&ouml;nliches</h2>
  <ul>
    <li><a href="Programmieren/index.html">OpenSource Programme</a></li>
    <li><a href="Bilder/index.htm">Bilder</a></li>
    <li><a href="sinnlos/index.html">Sinnlos</a></li>

    <li><a href="Links/index.html">Links</a></li>
    <li><a href="http://cgi6.ebay.de/ws/eBayISAPI.dll?ViewSellersOtherItems&amp;userid=jedie1024">meine privaten eBay Auktionen</a></li>
  </ul>
  <h2>Intern</h2>
  <p>Farbschema w&auml;hlen: <span id="cssAuswahl">&nbsp;</span><noscript>(funktioniert nur mit JavaScript!)</noscript></p>
  <ul>

    <li><a href="sitemap.html"> SiteMap</a></li>
    <li><form method="post" action="cgi-bin/PyWebSearch/PyWebSearch.py">Suche (BETA): <input type="text" name="SearchString" /><input type="submit" value="Finden" /></form></li>
    <li><a href="/SharedDATA/eMail/index.html" onclick="window.open('SharedDATA/eMail/index.html','eMail','width=460,height=370,dependent=no,location=no,menubar=no,status=no,toolbar=no');return false;">eMail an mich</a></li>
  </ul>
  <!-- InstanceEndEditable --> </div>
  <div class="backUnten2"><!-- InstanceBeginEditable name="backUnten" --><!-- InstanceEndEditable --></div>

  <!-- #BeginLibraryItem "/Library/LetzteÄnderung2.lbi" -->
  <div id="LetzteAenderung">Letzte &Auml;nderung:
    <!-- #BeginDate format:Ge1 -->28.02.2005<!-- #EndDate -->
    <a href="#" id="kommrein" class="LetzteAenderung">&nbsp;</a>
    <script src="SiteManagerJS/MakeLogInLink.js" type="text/javascript"></script>
    <noscript>
    </noscript>
  </div>

  <!-- #EndLibraryItem -->
  <script src="css/LinkManager.js" type="text/javascript"></script>
  <noscript>
  </noscript>
</div>
<h2>Jens Diemer</h2>

<p>Hier ist meine neue Homepage.</p>

<p>Noch ist allerdings <a href="hrefURL">nicht</a> alles fertig&#8230;</p>

<lucidTag:powered_by/>

<h3>Letzte &#195;&#132;nderungen:</h3>

<lucidFunction:IncludeRemote>http://jensdiemer.de/cgi-bin/PyLucid/ListOfNewSides.py</lucidFunction>
</body>
<!-- InstanceEnd --></html>
"""


if __name__ == "__main__":
    MyParser = MetaContentParser()
    MyParser.feed( TestTXT )
    MyParser.dump()