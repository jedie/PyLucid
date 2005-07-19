#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Editor für alles was mit aussehen zu tun hat:
    - edit_style
    - edit_template
    - edit_internal_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi



#_______________________________________________________________________
# Module-Manager Daten für den page_editor


class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "edit_style" : {
            "txt_menu"      : "edit style",
            "txt_long"      : "edit the CSS stylesheets",
            "section"       : "admin sub menu",
            "category"      : "edit look",
            "must_login"    : True,
            "must_admin"    : True,
        },
        "edit_template" : {
            "txt_menu"      : "edit template",
            "txt_long"      : "edit the HTML-code of the templates",
            "section"       : "admin sub menu",
            "category"      : "edit look",
            "must_login"    : True,
            "must_admin"    : True,
        },
        "edit_internal_page" : {
            "txt_menu"      : "edit internal page",
            "txt_long"      : "edit the HTML-code of the internal page",
            "section"       : "admin sub menu",
            "category"      : "misc",
            "must_login"    : True,
            "must_admin"    : True,
        },
    }



#_______________________________________________________________________


class edit_look:
    def __init__( self, PyLucid ):
        self.config     = PyLucid["config"]
        #~ self.config.debug()
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db         = PyLucid["db"]
        self.tools      = PyLucid["tools"]

    def action( self ):
        """FÃ¼hrt anhand der CGI-Daten die richtige Methode aus"""
        # Unteraktionen
        actions = {
            "edit_style" : [
                ( "edit",    self.edit_style ),
                ( "del",     self.del_style  ),
                ( "save",    self.save_style ),
            ],
            "edit_template" : [
                ( "edit",    self.edit_template ),
                ( "del",     self.del_template  ),
                ( "save",    self.save_template ),
            ],
            "edit_internal_page" : [
                ( "edit",    self.edit_internal_page ),
                ( "save",    self.save_internal_page ),
            ],
        }

        for command,data in actions.iteritems():
            if self.CGIdata["command"] == command:
                for sub_action,method in data:
                    if self.CGIdata.has_key( sub_action ):
                        return method( self.CGIdata[sub_action] )

        # Start-Aktion soll ausgefÃ¼hrt werden
        actions = [
            ("edit_style",          self.edit_style_select_page    ),
            ("edit_template",       self.edit_template_select_page ),
            ("edit_internal_page",  self.edit_internal_page_select ),
        ]
        for action,method in actions:
            if self.CGIdata["command"] == action:
                return method()
        return "<h1>internal error!</h1>"


    #_______________________________________________________________________
    ## Stylesheet

    def edit_style_select_page( self ):
        """ generiert Tabelle zur Style Auswahl """
        page  = "<h2>Edit styles</h2>"
        page += self.select_table(
            type        = "style",
            table_data  = self.db.get_style_list()
        )
        return page

    def edit_style( self, style_id ):
        """ Seite zum editieren eines Stylesheet """
        try:
            edit_data = self.db.get_style_data( style_id )
        except IndexError:
            return "bad style id!"

        return self.make_edit_page(
            edit_data           = edit_data,
            internal_page_name  = "edit_style",
            order               = "edit_style",
            id                  = style_id,
        )

    def save_style( self, style_id ):
        """ Speichert einen editierten Stylesheet """
        style_data = {
            "description"   : self.CGIdata["description"],
            "content"       : self.CGIdata["content"]
        }
        self.db.update_style( style_id, style_data )
        page = "<h3>Style saved!</h3>"
        page += self.edit_style_select_page()
        return page

    def del_style( self, style_id ):
        return "del_style not ready!"

    #_______________________________________________________________________
    ## Template

    def edit_template_select_page( self ):
        """ generiert eine Tabelle zur Template Auswahl """
        page  = "<h2>Edit template</h2>"
        page += self.select_table(
            type        = "template",
            table_data  = self.db.get_template_list()
        )
        return page

    def edit_template( self, template_id ):
        """ Seite zum editieren eines template """
        try:
            edit_data = self.db.get_template_data( template_id )
        except IndexError:
            return "bad template id!"

        return self.make_edit_page(
            edit_data           = edit_data,
            internal_page_name  = "edit_template",
            order               = "edit_template",
            id                  = template_id,
        )

    def save_template( self, template_id ):
        """ Speichert einen editierten template """
        template_data = {
            "description"   : self.CGIdata["description"],
            "content"       : self.CGIdata["content"]
        }
        self.db.update_template( template_id, template_data )
        page = "<h3>template saved!</h3>"
        page += self.edit_template_select_page()
        return page

    def del_template( self, template_id ):
        return "del_template not ready!"

    #_______________________________________________________________________
    ## Methoden fÃ¼r Stylesheet- und Template-Editing

    def make_edit_page( self, edit_data, internal_page_name, order, id ):
        """ Erstellt die Seite zum Stylesheet/Template editieren """

        internal_page   = self.db.get_internal_page(internal_page_name)["content"]

        back_url = "%s?command=%s" % ( self.config.system.real_self_url, order )
        form_url =            "%s&save=%s" % ( back_url, id )

        try:
            internal_page = internal_page % {
                "name"          : edit_data["name"],
                "url"           : form_url,
                "content"       : cgi.escape( edit_data["content"] ),
                "description"   : cgi.escape( edit_data["description"] ),
                "back"          : back_url,
            }
        except KeyError, e:
            return "<h1>generate internal Page fail:</h1><h4>KeyError:'%s'</h4>" % e

        return internal_page

    def select_table( self, type, table_data ):
        """ Erstellt die Tabelle zum auswÃ¤hlen eines Style/Templates """
        page = '<table id="edit_%s_select" class="edit_table">' % type
        for item in table_data:
            page += "<tr>"
            page += "<td>%s</td>" % item["name"]

            page += '<td><a href="%s?command=edit_%s&edit=%s">edit</a></td>' % (
                self.config.system.real_self_url, type, item["id"]
            )
            page += '<td><a href="%s?command=edit_%s&del=%s">del</a></td>' % (
                self.config.system.real_self_url, type, item["id"]
            )
            page += "<td>%s</td>" % item["description"]
            page += "</tr>"
        page += "</table>"
        return page

    #_______________________________________________________________________
    ## Interne Seiten editieren

    def edit_internal_page_select( self ):
        """ Tabelle zum auswÃ¤hlen einer Internen-Seite zum editieren """
        page_list = self.db.get_internal_page_list()

        page  = "<h2>Edit internal page</h2>"
        page += '<table id="edit_internal_pages_select" class="edit_table">'
        for item in page_list:
            page += "<tr>"
            page += "<td>%s</td>" % item["name"]

            page += '<td><a href="%s?command=edit_internal_page&edit=%s">edit</a></td>' % (
                self.config.system.real_self_url, item["name"]
            )
            page += "<td>%s</td>" % item["description"]
            page += "</tr>"
        page += "</table>"
        return page

    def edit_internal_page( self, internal_page_name ):
        """ Formular zum editieren einer internen Seite """
        try:
            # Daten der internen Seite, die editiert werden soll
            edit_data = self.db.get_internal_page_data( internal_page_name )
        except IndexError:
            return "bad internal-page id!"

        # Daten der interne Seite zum editieren der internen Seiten holen ;)
        edit_page   = self.db.get_internal_page("edit_internal_page")

        OptionMaker = self.tools.html_option_maker()
        markup_option   = OptionMaker.build_from_list( self.config.available_markups, edit_data["markup"] )

        back_url = "%s?command=edit_internal_page" % self.config.system.real_self_url
        form_url =                            "%s&save=%s" % ( back_url, internal_page_name )

        try:
            edit_page["content"] = edit_page["content"] % {
                "name"          : internal_page_name,
                "url"           : form_url,
                "content"       : cgi.escape( edit_data["content"] ),
                "description"   : cgi.escape( edit_data["description"] ),
                "markup_option" : markup_option,
                "back"          : back_url,
            }
        except KeyError, e:
            return "<h1>generate internal Page fail:</h1><h4>KeyError:'%s'</h4>" % e

        return edit_page["content"], edit_page["markup"]

    def save_internal_page( self, internal_page_name ):
        """ Speichert einen editierte interne Seite """
        page_data = {
            "content"       : self.CGIdata["content"],
            "description"   : self.CGIdata["description"],
            "markup"        : self.CGIdata["markup"],
        }
        self.db.update_internal_page( internal_page_name, page_data )
        page = "<h3>internal page saved!</h3>"
        page += self.edit_internal_page_select()
        return page


#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return edit_look( PyLucid ).action()