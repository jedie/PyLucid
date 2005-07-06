#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Eine kleine Version vom textile Parser
(stehen unter der GPL-License)
by jensdiemer.de

http://jensdiemer.de/index.php?TinyTextile

Links
-----
http://dealmeida.net/en/Projects/PyTextile/
http://www.solarorange.com/projects/textile/mtmanual_textile2.html
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1.6"

__history__="""
v0.1.6
    - neu: auch nummerierte Listen: <ol>...</ol>
v0.1.5
    - neu: interner PyLucid Link mit [[SeitenName]]
    - neu: small Text: --klein-- -> <small>klein</small>
v0.1.4
    - neu: img-Tag wird durch !/MeinBild.jpg! erzeugt
    - dank Joe, neue RE Regeln für das trennen einer Liste vom Text
v0.1.3
    - Im Pre-Process wird eine Liste direkt nach einem Text getrennt
v0.1.2
    - Fehler in generierung von Listen behoben
v0.1.1
    - Links werden nun richtig umgesetz: Dank an BlackJack
v0.1.0
    - erste Version
"""

__todo__ = """
    ToDo
    ----
mit [sc Datei] PyLucid/system/SourceCode.py benutzen
"""

import sys, re, cgi

SourceCodeParser = "/cgi-bin/PyLucid/system/SourceCode.py"



class parser:
    def __init__(self, out_obj, newline="\n" ):
        self.out        = out_obj
        self.newline    = newline

        # Regeln für Blockelemente
        self.block_rules = self._compile_rules( [
            [ # <h1>-Überschriften
                r"\Ah(\d)\. +(.*)(?us)",
                r"<h\1>\2</h\1>"
            ],
            [ # Sourcecode Hightligting
                r"\[sc (.*?)\](?us)",
                self.do_sourcecode
            ],
        ] )

        # Regeln für Inlineelemente
        self.inline_rules = self._compile_rules( [
            [ # Kleiner Text - Bsp.: Ich bin ein --kleines-- Wort.
                r"--(.+?)--",
                r"<small>\1</small>"
            ],
            [ # Fettschrift - Bsp.: Das Wort ist in *fett* geschrieben.
                r"\*([^* ]+?)\*(?uism)",
                r"<strong>\1</strong>"
            ],
            [ # img-Tag - Bsp.: !/Bilder/MeinBild.jpg!
                r'\!(.+?)\!(?uis)',
                r'<img src="\1">'
            ],
            [ # Link + LinkText - Bsp.: "LinkText":http://www.beispiel.de
                r'"(.+?)":(\S+)',
                r'<a href="\2">\1</a>'
            ],
            [ # interne PyLucid Links - Bsp.: Das ist ein [[InternerLink]] zur Seite InternerLink ;)
                r'\[\[(.+?)\]\]',
                r'<a href="?\1">\1</a>'
            ],
            [ # Link alleine im Text - Bsp.: Das wird ein Link: http://www.beispiel.de weil es eine URL ist
                r'''
                    (?<!=") # Ist noch kein HTML-Link
                    (?P<url>(http|ftp)://(\S+))
                    (?uimx)
                ''',
                r'<a href="\g<url>">\g<url></a>'
            ],
            [ # EMails
                r'mailto:(\S+)',
                r'<a href="mailto:\1">\1</a>'
            ],
        ] )

        # Pre-Process Regeln
        self.pre_process_rules = self._compile_rules( [
            [ # NewLines von Windows "\r\n", MacOS "\r" nach "\n" vereinheitlichen
                r"\r\n{0,1}",
                r"\n"
            ],
            [ # HTML-Escaping
                r"==(.+?)==(?usm)",
                self.escaping
            ],
            [ # Text vor einer Liste mit noch einem \n trennen
                r"""
                    (^[^*\n].+?$) # Text-Zeile vor einer Liste
                    (\n^\*) # Absatz + erstes List-Zeichen
                    (?uimx)
                """,
                r"\1\n\2",
            ],
        ] )

        self.pre_start = re.compile( r"(<pre>)" )
        self.pre_end = re.compile( r"(<\/pre>)" )

        self.is_html = re.compile( r"<.+?>" )

    def _compile_rules( self, rules ):
        "Kompliliert die RE-Ausdrücke"
        for rule in rules:
            rule[0] = re.compile( rule[0] )
        return rules

    def parse( self, txt ):
        "Parsed den Text in's out_obj"
        txt = self.pre_process( txt )
        self.make_paragraphs( txt )

    def escaping( self, matchobj ):
        return cgi.escape( matchobj.group(1) )

    def pre_process( self, txt ):
        "Vorab Verarbeitung des Textes"
        # Leerzeilen vorn und hinten abschneiden
        txt = txt.strip()

        # Preprocess rules anwenden
        for rule in self.pre_process_rules:
            txt = rule[0].sub( rule[1], txt )
        return txt

    def make_paragraphs( self, txt ):
        """
        Verarbeitung des Textes.
        Wendet Blockelement-Regeln und Inlineelement-Regeln an.
        """
        blocks = re.split("\n{2,}", txt)
        text = ""
        pre = False
        for block in blocks:
            #~ self.out.write( "-"*80 ) # Debug
            block = block.strip()
            if len(block) == 0:
                continue

            # pre-Tag, wird direkt ausgegeben
            if ( self.pre_end.findall(block)!=[] ):
                self.out.write( block + self.newline )
                pre=False
                continue
            if ( self.pre_start.findall(block)!=[] ) or ( pre == True ):
                self.out.write( block + self.newline )
                pre=True
                continue

            if self.is_html.findall( block ) != []:
                # Der Block scheint schon HTML-Code zu sein
                self.out.write( block + self.newline )
                continue

            # inline-rules Anwenden
            for inlinerule in self.inline_rules:
                #~ print ">>>",block,"<<<"
                block = inlinerule[0].sub( inlinerule[1], block )

            # Block-rules Anwenden
            self.blockelements( block )



    def blockelements( self, block ):
        "Anwenden der Block-rules. Formatieren des Absatzes"

        if block[0] in ("*","#"):
            # Aktueller Block ist eine eine Liste
            self.build_list( block )
            return

        for rule in self.block_rules:
            txt,count = rule[0].subn( rule[1], block )

            if count != 0:
                # Ein Blockelement wurde gefunden
                self.out.write( txt + self.newline )
                return

        # Kein Blockelement gefunden -> Formatierung des Absatzes
        block = block.strip().replace("\n", "<br />" + self.newline )
        self.out.write( "<p>%s</p>" % block + self.newline )

    def do_sourcecode( self, matchobj ):
        "Source Code-File der mittels PyLucid/system/SourceCode.py dagestellt werden soll"
        # ist nocht nicht fertig :(
        return "**** PyLucid/system/SourceCode.py %s ****" % matchobj.group(1)

    def build_list( self, listitems ):
        "Erzeugt eine Liste aus einem Absatz"

        def spacer( deep ): return " "* ( deep * 3 )

        def write( number, Tag, spacer ):
            for i in range( number ):
                self.out.write( spacer + Tag )

        deep = 0
        for item in re.findall( "([\*#]+) (.*)", listitems ):
            currentlen = len( item[0] )
            if item[0][0] == "*":
                # normale Aufzählungsliste
                pre_tag  = "<ul>"
                post_tag = "</ul>"
            else:
                # Nummerierte Liste
                pre_tag  = "<ol>"
                post_tag = "</ol>"

            if currentlen > deep:
                write( currentlen - deep, pre_tag, spacer(deep) )
                deep = currentlen
            elif currentlen < deep:
                write( deep - currentlen, post_tag, spacer(deep) )
                deep = currentlen

            self.out.write( "%s<li>%s</li>" % (spacer(deep), item[1]) )

        for i in range( deep ):
            self.out.write( post_tag )




syntax_help = """h1. Überschriften

Überschriften werden mit h1. eingeleitet:

<pre>
h1. h-1 Überschrift

h2. h-2 Überschrift
</pre>

Ergibt:

h1. h-1 Überschrift

h2. h-2 Überschrift

(Wichtig ist hierbei, das eine Leerzeile unter der Überschriftzeile bleibt.)

<hr>

h1. Textformatierung

<pre>
Ich bin ein --kleines-- Wort mit ==<small>==-Tag
Das wird ein *fettes* Wort mit ==<strong>==-Tag
</pre>

Ergibt:

Ich bin ein --kleines-- Wort mit ==<small>==-Tag
Das wird ein *fettes* Wort mit ==<strong>==-Tag

<hr>

h1. Links

Links werden nach folgendem Schema notiert:

<pre>
"LinkText":URL

Beispiele:
----------
http://keinserver.dtl
ftp://keinserver.dtl
mailto:name@beispiel.dtl
http://www.python-forum.de
oder besser: "Das deutsche Python-Forum":http://www.python-forum.de
Das wird auch ein "Link":?#unten
Ein interner PyLucid Link zur Seite [[BeispielSeitenName]]!
</pre>

Ergibt:
http://keinserver.dtl
ftp://keinserver.dtl
mailto:name@beispiel.dtl
http://www.python-forum.de
oder besser: "Das deutsche Python-Forum":http://www.python-forum.de
Das wird auch ein "Link":?#unten
Ein interner PyLucid Link zur Seite [[BeispielSeitenName]]!

<hr>

h1. Listen

Normale Listen werden mit einem "*" und nummerierte Liste mit einem "#"
eingeleitet. Diese können verschachtelt werden. Allerdings sollte man
keine normale und nummerierte Listen zusammen mischen.

<pre>
* 1. Eintrag in der erste Ebene
** 1. Unterprunkt in der zweiten Ebene
**** 1. Subunterpunkt in der vierter Ebene
**** 2. Subunterpunkt in der vierter Ebene
** 2. Unterprunkt in der zweiten Ebene

Nummerierte Liste:

# Nummer eins
# Nummer zweite
## und so...
## ...weiter...
</pre>

Ergibt:

* 1. Eintrag in der erste Ebene
** 1. Unterprunkt in der zweiten Ebene
**** 1. Subunterpunkt in der vierter Ebene
**** 2. Subunterpunkt in der vierter Ebene
** 2. Unterprunkt in der zweiten Ebene

Nummerierte Liste:

# Nummer eins
# Nummer zweite
## und so...
## ...weiter...

<hr>

h1. Bilder

Ein HTML-img-Tag wird erzeugt, wenn eine Adresse mit einem "!"-Zeichen
umschlossen ist.

<pre>
!/Bilder/MeinBild.jpg!
</pre>

Ergibt:

==<img src="/Bilder/MeinBild.jpg">==

<hr>

h1. SourceCode

SourceCode wird mittels "SiverCity":http://silvercity.sourceforge.net Dargestellt.
Dabei wird eine Lokale Datei geöffnet und geparsed:

<pre>
[sc /htdocs/source/MyPythonFile.py]
</pre>

Ergibt:

[sc /htdocs/source/MyPythonFile.py]

<hr>

h1. Escaping

In zwei "="-Zeichen eingeschlossener Text wird escaped.

Beispiel:
---------
========
Table: <table width="90%" border="0" align="center">
Link: <a href="URL">txt</a>
Input: <input type="submit" value="preview" />
========

Es geht aber auch innerhalb eines Fliesstextes:
Mit ========<a href="URL">txt</a>======== wird kein Link erzeugt.

<hr>

h1. pre-Formarted-Text

In ==<pre>==-Tag eingeschlossener Text wird nicht escaped und nicht formatiert.

<pre>
Beispiel:
---------
h2. Dies wird zu keiner HTML-Überschrift
<h3>Das ist eine manuell eingeleitete h3-Überschrift</h3>
* Dies bleibt normaler Text...
* ...und wird keine Liste
</pre>

<hr>

h1. HTML-Code

HTML-Code wird einfach so belassen wie es ist:

<h3>Dies ist eine Tabelle</h3>
<ul>
   <li>1. Eintrag in der erste Ebene</li>
   <ul>
      <li>1. Unterprunkt in der zweiten Ebene</li>
      <ul>
         <li>1. Subunterpunkt in der dritten Ebene</li>
         <li>2. Subunterpunkt in der dritten Ebene</li>
      </ul>
      <li>2. Unterprunkt in der zweiten Ebene</li>
   </ul>
   <li>2. Eintrag in der erste Ebene</li>
   <li>3. Eintrag in der erste Ebene</li>
</ul>

Hier kommt ein manueller Link zum: <a href="http://www.python-forum.de">Das deutsche Python-Forum</a>

"""

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

if __name__ == "__main__":
    class out:
        def __init__( self, write_helpfile = False ):
            self.write_helpfile = write_helpfile
            if self.write_helpfile:
                self.Helpfile = file( "tinyTextile.html", "w" )
                self.Helpfile.write( HelpFileHead )
            self.orig_stdout = sys.stdout

        def write( self, txt ):
            txt = "%s\n" % txt
            self.orig_stdout.write( txt )
            if self.write_helpfile:
                self.Helpfile.write( txt )

        def close( self ):
            if self.write_helpfile:
                self.Helpfile.write( HelpFileFoot )
                self.Helpfile.close()

    #~ sys.stdout = out()
    sys.stdout = out( write_helpfile = True )

    parser( sys.stdout ).parse( syntax_help )
    #~ parser( sys.stdout, newline="" ).parse( text )
    sys.stdout.close()
