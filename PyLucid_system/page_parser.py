#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Der Parser füllt eine CMS Seite mit leben ;)
Parsed die lucid-Tags/Funktionen, führt diese aus und fügt das Ergebnis in die Seite ein.
"""

__version__="0.1.4"

__history__="""
v0.1.4
    - apply_markup kommt mit markup id oder richtigen namen klar
v0.1.3
    - textile Parser erhält nun auch die PyLucid-Objekt. page_msg ist hilfreich zum debuggen des Parsers ;)
v0.1.2
    - Bug 1297263: "Can't use textile-Markup (maximum recursion limit exceeded)":
        Nun wird zuerst das Markup angewendet und dann erst die lucidTag's aufgelöst
v0.1.1
    - parser.handle_function(): toleranter wenn kein String vom Modul zurück kommt
    - Versionsnummer geändert
v0.1.0
    - Erste Version: Komplett neugeschrieben. Nachfolge vom pagerender.py
"""

__todo__ = """
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber die Seiten keine IDs,
sondern die richtigen Namen verwenden geht das leider noch nicht :(
"""

import sys, cgi, re, time

class parser:
    """
    Der Parser füllt alle bekannten lucid-Tags (lucidTag & lucidFunction) aus.
    """
    def __init__( self, PyLucid ):
        self.page_msg       = PyLucid["page_msg"]

        # self.module_manager --> Wird in der index.py setup_parser() hierhin "übertragen"

        self.tag_data = {} # "Statische" Tags-Daten

        # Tags die nicht bearbeitet werden:
        self.ignore_tag = ("page_msg","script_duration")


    def parse( self, content ):
        """
        Die Hauptfunktion.
        per re.sub() werden die Tags ersetzt
        """
        #~ print "OK", content
        if type(content)!=str:
            return "page_parser Error! Content not string. Content is type %s" % cgi.escape(str(type(content)))

        #~ start_time = time.time()
        #~ try:
        content = re.sub( "<lucidTag:(.*?)/?>", self.handle_tag, content )
        #~ except Exception, e:
            #~ print "ERROR:", e, content
            #~ return "ERROR:", e
        #~ self.page_msg( "Zeit (re.sub-lucidTag) :", time.time()-start_time )

        #~ start_time = time.time()
        #~ try:
        content = re.sub( "<lucidFunction:(.*?)>(.*?)</lucidFunction>", self.handle_function, content )
        #~ except Exception, e:
            #~ print "ERROR:", e, content
            #~ return "ERROR:", e
        #~ self.page_msg( "Zeit (re.sub-lucidFunction) :", time.time()-start_time )

        return content

    def handle_tag( self, matchobj ):
        """
        Abarbeiten eines <lucidTag:... />
        """
        #~ print matchobj.group(1)
        return_string = self.appy_tag( matchobj )
        if type(return_string) != str:
            self.page_msg("result of tag '%s' is not type string! Result: '%s'" % (
                    matchobj.group(1), cgi.escape( str(return_string) )
                )
            )

            return_string = str(return_string)
        #~ print "OK"
        return return_string

    def appy_tag( self, matchobj ):
        tag = matchobj.group(1)
        if tag in self.ignore_tag:
            # Soll ignoriert werden. Bsp.: script_duration, welches wirklich am ende
            # erst "ausgefüllt" wird ;)
            return matchobj.group(0)

        if self.tag_data.has_key( tag ):
            # Als "Statische" Information vorhanden
            return self.tag_data[tag]

        content = self.module_manager.run_tag(tag)
        if type(content) != str:
            content = "<p>[Content from module '%s' is not type string!] Content:</p>%s" % (
                function_name, str(content)
            )
        return content

        return matchobj.group(0)

    def handle_function( self, matchobj ):
        function_name = matchobj.group(1)
        function_info = matchobj.group(2)

        #~ print function_name, function_info

        content = self.module_manager.run_function( function_name, function_info )
        if type(content) != str:
            content = "<p>[Content from module '%s' is not type string!] Content:</p>%s" % (
                function_name, str(content)
            )
        return content



class render:
    """
    Parsed die Seite und wendes das Markup an.
    """
    def __init__( self, PyLucid ):
        self.PyLucid    = PyLucid
        self.page_msg   = PyLucid["page_msg"]
        self.CGIdata    = PyLucid["CGIdata"]
        self.config     = PyLucid["config"]
        self.session    = PyLucid["session"]
        self.parser     = PyLucid["parser"]
        self.tools      = PyLucid["tools"]
        self.db         = PyLucid["db"]


    def render( self, side_data ):

        side_content = self.apply_markup( side_data["content"], side_data["markup"] )

        self.parser.tag_data["page_name"]           = cgi.escape( side_data["name"] )
        self.parser.tag_data["page_title"]          = cgi.escape( side_data["title"] )
        self.parser.tag_data["page_last_modified"]  = self.tools.convert_date_from_sql(
            side_data["lastupdatetime"], format = "preferences"
        )
        self.parser.tag_data["page_datetime"]       = self.tools.convert_date_from_sql(
            side_data["lastupdatetime"], format = "DCTERMS.W3CDTF"
        )
        self.parser.tag_data["page_keywords"]       = side_data["keywords"]
        self.parser.tag_data["page_description"]    = side_data["description"]

        if self.CGIdata.has_key("command"):
            # Ein Kommando soll ausgeführt werden -> Interne Seite
            self.parser.tag_data["robots"] = self.config.system.robots_tag["internal_pages"]
        else:
            self.parser.tag_data["robots"] = self.config.system.robots_tag["content_pages"]

        # lucidTag's und lucidFunction's auflösen
        side_content = self.parser.parse( side_content )

        return side_content


    def apply_markup( self, content, markup ):
        """
        Wendet das Markup auf den Seiteninhalt an
        """
        # Die Markup-ID Auflösen zum richtigen Namen
        markup = self.db.get_markup_name( markup )

        if markup == "textile":
            # textile Markup anwenden
            if self.config.system.ModuleManager_error_handling == True:
                try:
                    from PyLucid_system import tinyTextile
                    out = self.tools.out_buffer()
                    tinyTextile.parser( out, self.PyLucid ).parse( content )
                    return out.get()
                except Exception, e:
                    self.page_msg( "Can't use textile-Markup (%s)" % e )
            else:
                from PyLucid_system import tinyTextile
                out = self.tools.out_buffer()
                tinyTextile.parser( out, self.PyLucid ).parse( content )
                return out.get()
        elif markup == "none" or markup == None or markup == "string formatting":
            return content
        else:
            self.page_msg( "Markup '%s' not supported yet :(" % markup )
            return content


    def apply_template( self, side_content, template ):
        """
        Alle Tags im Template ausfüllen und dabei die Seite in Template einbauen
        """
        self.parser.tag_data["page_body"]    = side_content

        side_content = self.parser.parse( template )

        return side_content