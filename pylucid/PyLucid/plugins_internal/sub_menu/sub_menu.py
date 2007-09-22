#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
<lucidTag:sub_menu/>
Generiert Links aller Unterseiten

Last commit info:
----------------------------------
$LastChangedDate: $
$Rev: $
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev: $"

# Python-Basis Module einbinden
import re, os, sys, urllib, cgi


from PyLucid.db.page import get_sub_menu_data
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page
from PyLucid.db.page import get_link_by_id

class sub_menu(PyLucidBasePlugin):

    def lucidTag( self ):
        """
        Display the sub menu
        """
        # Get a list of all sub pages from the database:
        sub_pages = get_sub_menu_data(self.request, self.current_page.id)

        context = {
            "sub_pages": sub_pages,
            "pre_link": self.current_page.get_absolute_url(),
        }
        self._render_template("sub_menu", context)#, debug=True)
















