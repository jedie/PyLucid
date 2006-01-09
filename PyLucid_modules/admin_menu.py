#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
Erzeugt das Administration-Menü
(ehemals front_menu aus dem alten page-renderer)

<lucidTag:admin_menu/>
Sollte im Template für jede Seite eingebunden werden.
"""

__version__="0.0.4"

__history__="""
v0.0.4
    - nutzt nun self.db.print_internal_page()
v0.0.3
    - Anpassung an wegfall von apply_markup
v0.0.2
    - lucidTag ist nicht mehr front_menu sondern admin_menu
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
#~ import



class admin_menu:

    def __init__( self, PyLucid ):
        self.db         = PyLucid["db"]
        self.page_msg   = PyLucid["page_msg"]
        self.config     = PyLucid["config"]
        self.CGIdata    = PyLucid["CGIdata"]
        self.URLs       = PyLucid["URLs"]

    def lucidTag( self ):
        """
        Front menu anzeigen
        """
        try:
            self.db.print_internal_page("admin_menu_top_menu")
        except Exception, e:
            print "[Error: Can't print internal page: %s]" % e

    def edit_page_link( self ):
        print '<a href="%s&amp;command=pageadmin&amp;action=edit_page">edit page</a>' % self.URLs["base"]

    def new_page_link( self ):
        print '<a href="%s&amp;command=pageadmin&amp;action=new_page">new page</a>' % self.URLs["base"]

    def sub_menu_link( self ):
        print '<a href="%ssub_menu">sub menu</a>' % self.URLs["action"]

    def sub_menu( self ):
        return self.db.get_internal_page("admin_menu_sub_menu")
