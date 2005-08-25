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

__version__="0.0.3"

__history__="""
v0.0.3
    - Bug: Edit Template: http://sourceforge.net/tracker/index.php?func=detail&aid=1273348&group_id=146328&atid=764837
v0.0.2
    - NEU: Clonen von Stylesheets und Templates nun möglich
    - NEU: Löschen von Stylesheets und Templates geht nun
    - Änderung der "select"-Tabellen, nun Anpassung per CSS möglich
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi



#_______________________________________________________________________
# Module-Manager Daten f�r den page_editor


class module_info:
    """Pseudo Klasse: Daten f�r den Module-Manager"""
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
            "category"      : "edit look",
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
        self.page_msg   = PyLucid["page_msg"]

    def action( self ):
        """Führt anhand der CGI-Daten die richtige Methode aus"""
        # Unteraktionen
        actions = {
            "edit_style" : [
                ( "edit",       self.edit_style ),
                ( "del",        self.del_style  ),
                ( "duplicate",  self.copy_style ),
                ( "save",       self.save_style ),
            ],
            "edit_template" : [
                ( "edit",       self.edit_template ),
                ( "del",        self.del_template  ),
                ( "duplicate",  self.copy_template ),
                ( "save",       self.save_template ),
            ],
            "edit_internal_page" : [
                ( "edit",       self.edit_internal_page ),
                ( "save",       self.save_internal_page ),
            ],
        }

        # Unteraktion starten
        for command,data in actions.iteritems():
            if self.CGIdata["command"] == command:
                for sub_action,method in data:
                    if self.CGIdata.has_key( sub_action ):
                        method( self.CGIdata[sub_action] )
                        return

        # Start-Aktion soll ausgeführt werden
        actions = [
            ("edit_style",          self.edit_style_select_page    ),
            ("edit_template",       self.edit_template_select_page ),
            ("edit_internal_page",  self.edit_internal_page_select ),
        ]
        for action,method in actions:
            if self.CGIdata["command"] == action:
                method()
                return

        print "<h1>internal error!</h1>"
        return

    #_______________________________________________________________________
    ## Stylesheet

    def edit_style_select_page( self ):
        """ generiert Tabelle zur Style Auswahl """
        print "<h2>Edit styles</h2>"
        self.select_table(
            type        = "style",
            table_data  = self.db.get_style_list()
        )

    def edit_style( self, style_id ):
        """ Seite zum editieren eines Stylesheet """
        try:
            edit_data = self.db.get_style_data( style_id )
        except IndexError:
            print "bad style id!"
            return

        self.make_edit_page(
            edit_data           = edit_data,
            internal_page_name  = "edit_style",
            order               = "edit_style",
            id                  = style_id,
        )

    def copy_style( self, dummy ):
        """ Ein Stylesheet soll kopiert werden """
        try:
            clone_name  = self.CGIdata["clone_name"]
            new_name    = self.CGIdata["new_name"]
        except KeyError:
            print "Error in Data!"
            return

        style_content = self.db.get_style_data_by_name( clone_name )["content"]

        style_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : style_content,
        }
        self.db.new_style( style_data )

        self.page_msg( "style '%s' duplicated to '%s'" % (clone_name, new_name) )
        self.edit_style_select_page()

    def save_style( self, style_id ):
        """ Speichert einen editierten Stylesheet """
        style_data = {
            "description"   : self.CGIdata["description"],
            "content"       : self.CGIdata["content"]
        }
        self.db.update_style( style_id, style_data )
        self.page_msg( "Style saved!" )
        self.edit_style_select_page()

    def del_style( self, style_id ):
        """ Lösche ein Stylesheet """
        self.page_msg( "Delete Style (id:'%s')" % style_id )
        self.db.delete_style( style_id )
        self.edit_style_select_page()

    #_______________________________________________________________________
    ## Template

    def edit_template_select_page( self ):
        """ generiert eine Tabelle zur Template Auswahl """
        print "<h2>Edit template</h2>"
        self.select_table(
            type        = "template",
            table_data  = self.db.get_template_list()
        )

    def edit_template( self, template_id ):
        """ Seite zum editieren eines template """
        try:
            edit_data = self.db.get_template_data( template_id )
        except IndexError:
            print "bad template id!"
            return

        self.make_edit_page(
            edit_data           = edit_data,
            internal_page_name  = "edit_template",
            order               = "edit_template",
            id                  = template_id,
        )

    def copy_template( self, dummy ):
        """ Ein Template soll kopiert werden """
        try:
            clone_name  = self.CGIdata["clone_name"]
            new_name    = self.CGIdata["new_name"]
        except KeyError:
            print "Error in Data!"
            return

        template_content = self.db.get_template_data_by_name( clone_name )["content"]

        template_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : template_content,
        }
        self.db.new_template( template_data )

        self.page_msg( "template '%s' duplicated to '%s'" % (clone_name, new_name) )
        self.edit_template_select_page()

    def save_template( self, template_id ):
        """ Speichert einen editierten template """
        template_data = {
            "description"   : self.CGIdata["description"],
            "content"       : self.CGIdata["content"]
        }
        self.db.update_template( template_id, template_data )
        print "<h3>template saved!</h3>"
        self.edit_template_select_page()

    def del_template( self, template_id ):
        """ Lösche ein Template """
        self.page_msg( "Delete Template (id:'%s')" % template_id )
        self.db.delete_template( template_id )
        self.edit_template_select_page()

    #_______________________________________________________________________
    ## Methoden für Stylesheet- und Template-Editing

    def make_edit_page( self, edit_data, internal_page_name, order, id ):
        """ Erstellt die Seite zum Stylesheet/Template editieren """

        internal_page   = self.db.get_internal_page(internal_page_name)["content"]

        back_url = "%s?command=%s" % ( self.config.system.real_self_url, order )
        form_url =            "%s&save=%s" % ( back_url, id )

        try:
            print internal_page % {
                "name"          : edit_data["name"],
                "url"           : form_url,
                "content"       : cgi.escape( edit_data["content"] ),
                "description"   : cgi.escape( edit_data["description"] ),
                "back"          : back_url,
            }
        except KeyError, e:
            print "<h1>generate internal Page fail:</h1><h4>KeyError:'%s'</h4>" % e
            return

    def select_table( self, type, table_data ):
        """ Erstellt die Tabelle zum auswählen eines Style/Templates """

        form_tag = '<form name="edit_%s" method="post" action="%s?command=edit_%s">' % (
            type, self.config.system.real_self_url, type#, self.CGIdata["page_id"]
        )

        print form_tag
        print 'Duplicate <select name="clone_name">'
        print self.tools.html_option_maker().build_from_list( [i["name"] for i in table_data] )
        print '</select> to a new %s named: ' % type
        print '<input name="new_name" value="" size="20" maxlength="50" type="text">'
        print '<button type="submit" name="duplicate" value="True">clone</button>'
        print '</form>'

        print form_tag
        print '<table id="edit_%s_select" class="edit_table">' % type

        JS = '''onclick="return confirm('Are you sure to delete the item ?')"'''

        for item in table_data:
            print "<tr>"
            print '<td>'
            print '<span class="name">%s</span><br/>' % item["name"]
            print '<span class="description">%s</span>' % item["description"]
            print "</td>"

            print '<td><button type="submit" name="edit" value="%s">edit</button></td>' % item["id"]
            print '<td><button type="submit" name="del" value="%s" %s>del</button></td>' % (
                item["id"], JS
            )

            print "</tr>"
        print '</table></form>'

    #_______________________________________________________________________
    ## Interne Seiten editieren

    def edit_internal_page_select( self ):
        """ Tabelle zum auswählen einer Internen-Seite zum editieren """
        print "<h2>Edit internal page</h2>"
        print '<table id="edit_internal_pages_select" class="edit_table">'

        page_list = self.db.get_internal_page_list()
        for item in page_list:
            print "<tr>"
            print "<td>%s</td>" % item["name"]

            print '<td><a href="%s?command=edit_internal_page&edit=%s">edit</a></td>' % (
                self.config.system.real_self_url, item["name"]
            )
            print "<td>%s</td>" % item["description"]
            print "</tr>"
        print "</table>"

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
        try:
            page_data = {
                "content"       : self.CGIdata["content"],
                "description"   : self.CGIdata["description"],
                #~ "markup"        : self.CGIdata["markup"],
            }
        except KeyError,e:
            return self.error(
                "Formdata not complete.", e, "set internal Pages to default with install_PyLucid.py",
                "use back-Button!"
            )
        self.db.update_internal_page( internal_page_name, page_data )

        print "<h3>internal page saved!</h3>"
        print self.edit_internal_page_select()

    #_______________________________________________________________________
    ## Allgemeine Funktionen

    def error( *msg ):
        page  = "<h2>Error.</h2>"
        page += "<p>%s</p>" % "<br/>".join( [str(i) for i in msg] )
        return page

#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return edit_look( PyLucid ).action()