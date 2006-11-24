#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
preferences

Hält die Grundeinstellungen vor, die in der config middleware gespeichert sind.

Bietet Methoden an um die Einstellungen in der DB zu ändern.
"""

import UserDict

from PyLucid.system.exceptions import *



class Preferences(UserDict.UserDict):
    def __init__(self, config_middleware):
        self.data = config_middleware # Grundconfig

    def init2(self,request, response):
        self.request    = request
        self.response   = response

        # shorthands
        #~ self.runlevel       = request.runlevel
        #~ self.session        = request.session
        #~ self.preferences    = request.preferences
        #~ self.URLs           = request.URLs
        #~ self.log            = request.log
        #~ self.module_manager = request.module_manager
        #~ self.tools          = request.tools
        #~ self.render         = request.render
        #~ self.tag_parser     = request.tag_parser
        #~ self.staticTags     = request.staticTags
        #~ self.templates      = request.templates

        self.page_msg       = response.page_msg
        self.db             = request.db

    def update_from_sql(self, db):
        """ Preferences aus der DB lesen und in self speichern """

        RAWdata = db.get_all_preferences()

        if RAWdata == None:
            raise ProbablyNotInstalled("No preferences in database!")

        for line in RAWdata:
            # Die Values sind in der SQL-Datenbank als Type varchar() angelegt.
            # Doch auch Zahlenwerte sind gespeichert, die PyLucid doch lieber
            # auch als Zahlen sehen möchte ;)
            try:
                line["value"] = int(line["value"])
            except ValueError:
                pass

            section = line["section"]
            if not section in self.data:
                # Neue Sektion
                self.data[section] = {}

            self.data[section][line["varName"]] = line["value"]

    #_________________________________________________________________________

    def get_default_style_name(self):
        id = self["core"]["defaultStyle"]
        stylename = self.db.get_stylename_by_id(id)
        return stylename

    def set_default_style(self, name):
        try:
            style_id = self.db.get_style_id_by_name(name)
            self.set("core", "defaultStyle", style_id)
        except Exception, e:
            self.page_msg.red(
                "Can't set default style to '%s': %s" % (name, e)
            )
        else:
            self.page_msg.green("Set default style to '%s', OK" % name)

    #_________________________________________________________________________

    def get_default_template_name(self):
        id = self["core"]["defaultTemplate"]
        templatename = self.db.get_templatename_by_id(id)
        return templatename

    def set_default_template(self, name):
        try:
            template_id = self.db.get_template_id_by_name(name)
            self.set("core", "defaultTemplate", template_id)
        except Exception, e:
            self.page_msg.red(
                "Can't set default template to '%s': %s" % (name, e)
            )
        else:
            self.page_msg.green("Set default template to '%s', OK" % name)

    #_________________________________________________________________________

    def get_default_markup_id(self):
        id = self["core"]["defaultMarkup"]
        return id

    #_________________________________________________________________________


    def set(self, section, varName, value):
        self[section][varName] = value
        self.db.set_preferences(section, varName, value)




