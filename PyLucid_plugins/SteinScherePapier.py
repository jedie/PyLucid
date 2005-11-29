#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__url__ = "http://www.python-forum.de/viewtopic.php?t=4170"

import random


class SteinScherePapier:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
            "CGI_dependent_actions" : {
                "result"   : {
                    "CGI_must_have"      : ("ssp",)
                },
            }
        }
    }

    #_______________________________________________________________________

    def __init__(self, PyLucid):
        self.CGIdata    = PyLucid["CGIdata"]
        self.page_msg   = PyLucid["page_msg"]

    def lucidTag(self):
        print '<form method="post" action="%s">' % self.main_action_url
        print '  <p>Schere, Stein oder Papier?<br />'
        print '  <input type="radio" name="ssp" value="Schere"> Schere<br>'
        print '  <input type="radio" name="ssp" value="Stein"> Stein<br>'
        print '  <input type="radio" name="ssp" value="Papier"> Papier<br>'
        print '  <input type="submit" value="Go!">'
        print '  </p>'
        print '</form>'

    def result(self):
        # computer's choice and player's choice
        answer_dict = {1: "Schere", 2: "Stein", 3: "Papier"}
        cc = answer_dict[random.randint(1,3)]
        self.page_msg("Computer wählt: %s" % cc)

        pc = self.CGIdata["ssp"]

        if cc == pc:
            self.page_msg("Unentschieden!")
        elif cc == "Schere" and pc == "Stein":
            self.page_msg("Gewonnen! Stein schlägt Schere!")
        elif cc == "Schere" and pc == "Papier":
            self.page_msg("Verloren! Schere schlägt Papier!")
        elif cc == "Stein" and pc == "Schere":
            self.page_msg("Verloren! Stein schlägt Schere!")
        elif cc == "Stein" and pc == "Papier":
            self.page_msg("Gewonnen! Papier schlägt Schere!")
        elif cc == "Papier" and pc == "Schere":
            self.page_msg("Gewonnen! Schere schlägt Papier!")
        else:
            self.page_msg("Verloren! Papier schlägt Stein!")

        print "<h2>Neues Spiel?</h2>"

        # form wieder anzeigen
        self.lucidTag()
        return
