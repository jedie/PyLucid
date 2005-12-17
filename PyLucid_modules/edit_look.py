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

__version__="0.2"

__history__="""
v0.2
    - Bug 1308063: Umstellung von <button> auf <input>, weil's der IE nicht kann
        s. http://www.python-forum.de/viewtopic.php?t=4180
    - NEU: Styles und Template könnne nur dann gelöscht werden, wenn keine Seite diese noch benutzten
v0.1.1
    - edit_internal_page_form: markups sind nun IDs aus der Tabelle markups
v0.1.0
    - Komplettumbau für neuen Module-Manager
v0.0.4
    - Bug: Internal-Page Edit geht nun wieder
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




class edit_look:

    def __init__( self, PyLucid ):
        self.config     = PyLucid["config"]
        #~ self.config.debug()
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db         = PyLucid["db"]
        self.tools      = PyLucid["tools"]
        self.page_msg   = PyLucid["page_msg"]
        self.URLs       = PyLucid["URLs"]

    #_______________________________________________________________________
    ## Stylesheet

    def stylesheet( self ):
        """ Es wird die internal_page 'select_style' zusammen gebaut """
        self.select_table(
            type        = "style",
            table_data  = self.db.get_style_list()
        )

    def edit_style( self, id ):
        """ Seite zum editieren eines Stylesheet """
        try:
            edit_data = self.db.get_style_data( id )
        except IndexError:
            print "bad style id!"
            return

        self.make_edit_page(
            edit_data   = edit_data,
            name        = "edit_style",
            order       = "select_style",
            id          = id,
        )

    def clone_style( self, clone_name, new_name="NoName" ):
        """ Ein Stylesheet soll kopiert werden """

        style_content = self.db.get_style_data_by_name( clone_name )["content"]

        style_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : style_content,
        }
        try:
            self.db.new_style( style_data )
        except Exception, e:
            self.page_msg("Error clone Style '%s' to '%s': %s" % (clone_name, new_name, e) )
        else:
            self.page_msg( "style '%s' duplicated to '%s'" % (clone_name, new_name) )

        self.stylesheet() # Auswahlseite wieder anzeigen

    def save_style(self, id, name, description="", content=""):
        """ Speichert einen editierten Stylesheet """
        try:
            self.db.update_style( id, {"name": name, "content": content, "description": description} )
        except Exception, e:
            self.page_msg("Error saving style with id '%s' (use browser back button!): %s" % (id, e))
        else:
            self.page_msg( "Style saved!" )

        self.stylesheet() # Auswahlseite wieder anzeigen

    def del_style( self, id ):
        """ Lösche ein Stylesheet """
        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = ("style", id)
        )
        if page_names != ():
            names = [cgi.escape(i["name"]) for i in page_names]
            self.page_msg("Can't delete stylesheet, the following pages used it: %s" % names)
        else:
            try:
                self.db.delete_style( id )
            except Exception, e:
                self.page_msg("Error deleting style with id '%s': %s" % (id, e))
            else:
                self.page_msg( "Delete Style (id:'%s')" % id )

        self.stylesheet() # Auswahlseite wieder anzeigen

    #_______________________________________________________________________
    ## Template

    def template(self):
        """ Es wird die internal_page 'select_template' zusammen gebaut """
        self.select_table(
            type        = "template",
            table_data  = self.db.get_template_list()
        )

    def edit_template(self, id):
        """ Seite zum editieren eines template """
        try:
            edit_data = self.db.get_template_data(id)
        except IndexError:
            print "bad template id!"
            return

        self.make_edit_page(
            edit_data   = edit_data,
            name        = "edit_template",
            order       = "edit_template",
            id          = id,
        )

    def clone_template(self, clone_name, new_name="NoName"):
        """ Ein Template soll kopiert werden """
        template_content = self.db.get_template_data_by_name( clone_name )["content"]

        template_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : template_content,
        }
        try:
            self.db.new_template( template_data )
        except Exception, e:
            self.page_msg("Error cloning %s to %s: %s" % (clone_name, new_name, e))
        else:
            self.page_msg("template '%s' duplicated to '%s'" % (clone_name, new_name))

        self.template() # Auswahlseite wieder anzeigen

    def save_template(self, id, name, description="", content=""):
        """ Speichert einen editierten template """
        try:
            self.db.update_template( id, {"name": name, "description": description, "content": content} )
        except Exception, e:
            self.page_msg("Can't update template: %s" % e)
        else:
            self.page_msg("template with ID %s saved!" % id)

        self.template() # Auswahlseite wieder anzeigen

    def del_template(self, id):
        """ Lösche ein Template """
        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = ("template", id)
        )
        if page_names != ():
            names = [cgi.escape(i["name"]) for i in page_names]
            self.page_msg("Can't delete template, the following pages used it: %s" % names)
        else:
            try:
                self.db.delete_template(id)
            except Exception, e:
                self.page_msg("Error deleting template with id '%s': %s" % (id, e))
            else:
                self.page_msg("Delete Template (id:'%s')" % id)

        self.template() # Auswahlseite wieder anzeigen

    #_______________________________________________________________________
    ## Methoden für Stylesheet- und Template-Editing

    def make_edit_page( self, edit_data, name, order, id ):
        """ Erstellt die Seite zum Stylesheet/Template editieren """
        self.db.print_internal_page(
            internal_page_name  = name,
            page_dict           = {
                "name"          : edit_data["name"],
                "url"           : self.URLs["main_action"],
                "content"       : cgi.escape( edit_data["content"] ),
                "description"   : cgi.escape( edit_data["description"] ),
                "back"          : "%s%s" % (self.URLs["action"], order),
                "id"            : id,
            }
        )

    def select_table( self, type, table_data ):
        """ Erstellt die Tabelle zum auswählen eines Style/Templates """

        clone_select = self.tools.html_option_maker().build_from_list( [i["name"] for i in table_data] )

        table = '<table>\n'
        JS = '''onclick="return confirm('Are you sure to delete the item ?')"'''
        for item in table_data:
            table += "<tr>\n"
            table += '  <form name="edit_%s" method="post" action="%s">\n' % (item["name"], self.URLs["main_action"])
            table += '  <input name="id" type="hidden" value="%s">' % item["id"]
            table += '  <td class="name">%s</td>\n' % item["name"]
            table += '  <td class="description">%s</td>\n' % item["description"]
            table += '  <td><input type="submit" value="edit" name="edit" /></td>\n'
            table += '  <td><input type="submit" value="del" name="del" /></td>\n'
            table += "  </form>\n"
            table += "</tr>\n"
        table += '</table>\n'

        # Seite anzeigen
        self.db.print_internal_page(
            internal_page_name  = "select_%s" % type,
            page_dict           = {
                "main_action_url"   : self.URLs["main_action"],
                "clone_select"      : clone_select,
                "select_table"      : table,
            }
        )

    #_______________________________________________________________________
    ## Interne Seiten editieren

    def internal_page( self ):
        """ Tabelle zum auswählen einer Internen-Seite zum editieren """
        category_list   = self.db.get_internal_category()
        page_dict       = self.db.get_internal_page_dict()

        select_table = ""
        for category in category_list:
            printed_head = False
            for page_name, page in dict(page_dict).iteritems():
                if page["plugin_id"] == category["id"]:
                    if printed_head==False:
                        select_table += "<h3>%s</h3>\n" % category["module_name"].replace("_"," ")
                        select_table += '<table id="edit_internal_pages_select">\n'
                        printed_head=True
                    select_table += "<tr>\n"
                    select_table += '  <form name="internal_page" method="post" action="%s">\n' % self.URLs["main_action"]
                    select_table += '  <input name="internal_page_name" type="hidden" value="%s" />\n' % page_name
                    select_table += '  <td><input type="submit" value="edit" name="edit" /></td>\n'
                    select_table += '  <td class="name">%s</td>\n' % page["name"]
                    select_table += '  <td>%s</td>\n' % page["description"]
                    select_table += '  </form>\n'
                    select_table += "</tr>\n"
                    del page_dict[page_name]
            select_table += "</table>\n"

        if len(page_dict)>0:
            select_table += "<hr>"
            select_table += "<h3>in no category!</h3>\n"
            select_table += '<table id="edit_internal_pages_select">\n'
            for page_name, page in page_dict.iteritems():
                select_table += "<tr>\n"
                select_table += '  <form name="internal_page" method="post" action="%s">\n' % self.URLs["main_action"]
                select_table += '  <input name="internal_page_name" type="hidden" value="%s" />\n' % page_name
                select_table += '  <td><input type="submit" value="edit" name="edit" /></td>\n'
                select_table += '  <td class="name">%s</td>\n' % page["name"]
                select_table += '  <td class="name">%s</td>\n' % page["plugin_id"]
                select_table += '  <td>%s</td>\n' % page["description"]
                select_table += '  </form>\n'
                select_table += "</tr>\n"
            select_table += "</table>\n"

        self.db.print_internal_page(
            internal_page_name = "select_internal_page",
            page_dict = {
                "select_table" : select_table,
            }
        )

        print "<p><small>(edit_look v%s)</small></p>" % __version__

    def edit_internal_page(self, internal_page_name):
        """ Formular zum editieren einer internen Seite """
        try:
            # Daten der internen Seite, die editiert werden soll
            edit_data = self.db._get_internal_page_data( internal_page_name )
        except IndexError:
            self.page_msg( "bad internal-page name: '%s' !" % cgi.escape(internal_page_name) )
            self.internal_page() # Auswahl wieder anzeigen lassen
            return

        OptionMaker = self.tools.html_option_maker()
        markup_option   = OptionMaker.build_from_list(self.db.get_available_markups(), edit_data["markup"])

        self.db.print_internal_page(
            internal_page_name  = "edit_internal_page",
            page_dict           = {
                "name"          : internal_page_name,
                "url"           : self.URLs["main_action"],
                "content"       : cgi.escape( edit_data["content"] ),
                "description"   : cgi.escape( edit_data["description"] ),
                "markup_option" : markup_option,
                "back"          : "%sedit_internal_page" % self.URLs["action"],
            }
        )

    def save_internal_page(self, internal_page_name, content, description, markup):
        """ Speichert einen editierte interne Seite """
        page_data = {
            "content"       : content,
            "description"   : description,
            "markup"        : markup,
        }
        try:
            self.db.update_internal_page( internal_page_name, page_data )
        except Exception, e:
            self.page_msg("Error saving internal page '%s': %s" % (cgi.escape(internal_page_name), e))
        else:
            self.page_msg("internal page '%s' saved!" % cgi.escape(internal_page_name))

        self.internal_page() # Auswahl wieder anzeigen lassen

    #_______________________________________________________________________
    ## Allgemeine Funktionen

    def error( *msg ):
        page  = "<h2>Error.</h2>"
        page += "<p>%s</p>" % "<br/>".join( [str(i) for i in msg] )
        return page

