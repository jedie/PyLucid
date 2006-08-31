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



from PyLucid.system.BaseModule import PyLucidBaseModule

class admin_menu(PyLucidBaseModule):

    def lucidTag( self ):
        """
        Front menu anzeigen
        """
        context = {
            "login": self.request.staticTags['script_login'],
            "edit_page_link": self.URLs.commandLink("pageadmin", "edit_page"),
            "new_page_link": self.URLs.commandLink("pageadmin", "new_page"),
            "sub_menu_link": self.URLs.commandLink("admin_menu", "sub_menu"),
        }
        self.templates.write("top_menu", context)

    def sub_menu( self ):

        context = {"commandURLprefix": self.URLs["commandBase"]}
        #~ self.page_msg(context)

        self.templates.write("sub_menu", context)








