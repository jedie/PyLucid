#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:list_of_new_sides />
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.4"

__history__="""
v0.4
    - nutzt nun self.db.get_page_update_info() (nutzt auch der RSS Generator!)
v0.3
    - Erweitert: zeigt nun an, wer die Änderunen vorgenommen hat.
    - Nutzt ein jinja Template.
    - Zeigt nun immer die letzten 10 Änderungen, statt 5.
v0.2
    - Anpassung an v0.7
v0.1.1
    - Bugfix: URLs heißt das und nicht URL
v0.1.0
    - Anpassung an neuen Modul-Manager
v0.0.5
    - Anpassung an neuer Absolute-Seiten-Addressierung
v0.0.4
    - Bugfix: SQL Modul wird anders eingebunden
v0.0.3
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.2
    - Anpassung an neue SQL.py Version
    - Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version
"""




# Python-Basis Module einbinden
import cgi, re


from PyLucid.system.BaseModule import PyLucidBaseModule


class list_of_new_sides(PyLucidBaseModule):

    def lucidTag(self):
        """
        Aufruf über <lucidTag:list_of_new_sides />
        """
        page_updates = self.db.get_page_update_info(10)

        context = {
            "page_updates" : page_updates
        }
        #~ self.page_msg(context)

        self.templates.write("PageUpdateTable", context)













