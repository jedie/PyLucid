#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)


"""
Beispielmodul
-------------

Um dieses Modul zu benutzten einfach in einer CMS-Seite das folgende Tag einbauen:

<lucidTag:_example/>
"""


__version__="0.1.0"

__history__="""
v0.1.0
    - angepasst an neuen ModulManager
v0.0.1
    - erste Version
"""


class _example:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "methode1" : {
            "must_login"    : False,
            "must_admin"    : False,
        },
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        """
        Eine __init__ Methode muß immer vorhanden sein, da immer
        alle PyLucid-Objekte übergeben werden. Aus denen kann man sich
        dann benötigte rauspicken ;)
        """
        self.CGIdata = PyLucid["CGIdata"]

    def methode1( self ):
        """
        eine Minimales Beispiel
        """
        print "Hello World!"






