#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einstellungsdaten für Plugins/Module


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

#~ debug = True
debug = False

import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle


class PluginConfig(object):
    _cache = {}
    _modified = {}
    _current_section = "main"

    def __init__(self, request, response,
                        module_id, module_name, method_name="[not given]"):
        self.request    = request
        self.response   = response

        # shorthands
        self.environ        = request.environ
        self.page_msg       = response.page_msg
        self.db             = request.db
        self.session        = request.session

        #~ self.runlevel       = request.runlevel
        #~ self.preferences    = request.preferences
        #~ self.URLs           = request.URLs
        #~ self.log            = request.log
        #~ self.module_manager = request.module_manager
        #~ self.tools          = request.tools
        #~ self.render         = request.render
        #~ self.tag_parser     = request.tag_parser
        #~ self.staticTags     = request.staticTags
        #~ self.templates      = request.templates

        self.module_id = int(module_id) # type long brauchen wir nicht ;)
        self.module_name = module_name
        self.method_name = method_name

        #~ self.page_msg("plugin_cfg for:", module_id, module_name, method_name)

    #_________________________________________________________________________

    def __getitem__(self, key):
        try:
            return self._get_current_dict()[key]
        except KeyError, e:
            msg = "KeyError: '%s' not found in '%s'-plugin_cfg." % (
                e, self.module_name
            )
            raise KeyError(msg)

    def get(self, key, failobj=None):
        data = self._get_current_dict()
        if not data.has_key(key):
            return failobj
        return data[key]

    def __repr__(self):
        repr_string = repr(self._get_current_dict())
        return (
            "plugin_cfg - current module '%s', current section '%s'"
            " - data: %s"
        ) % (self.module_name, self._current_section, repr_string)

    def __contains__(self, key):
        try:
            return key in self._get_current_dict()
        except EntrieNotFound:
            return False

    def __setitem__(self, key, item):
        if debug: self.page_msg("Set key '%s' to '%s" % (key, item))
        current_dict = self._get_current_dict()
        if key in current_dict and current_dict[key] == item:
            # Keine Änderung
            return

        current_dict[key] = item
        if not self.module_id in self._modified:
            self._modified[self.module_id] = []
        self._modified[self.module_id].append(self._current_section)

    #_________________________________________________________________________

    def _get_from_db(self):
        if debug: self.page_msg("Get data from db:")
        try:
            data = self.db.select(
                select_items    = ["pickled_data"],
                from_table      = "plugin_cfg",
                where           = [
                    ("plugin_id", self.module_id),
                    ("section", self._current_section)
                ]
            )[0]["pickled_data"]
        except (IndexError, KeyError):
            msg = (
                "Can't get plugin_cfg for module '%s' (id: %s) from db"
            ) % (self.module_name, self.module_id)
            raise EntrieNotFound(msg)

        data = data.tostring() # Aus der DB kommt ein array Objekt!
        data = pickle.loads(data)
        if debug: self.page_msg(data)
        return data

    def _get_current_dict(self):
        try:
            return self._cache[self.module_id][self._current_section]
        except KeyError:
            # Ist noch nicht im cache, dann holen wir es aus der db
            pass

        data = self._get_from_db()

        if not self.module_id in self._cache:
            self._cache[self.module_id] = {}

        self._cache[self.module_id][self._current_section] = data
        return data

    def set_section(self, section_name):
        self._current_section = section_name

    #_________________________________________________________________________

    def commit(self):
        """
        Evtl. geänderte Daten sollen in die DB geschrieben werden
        """
        if not self.module_id in self._modified:
            # In diesem Module wurde nichts geändert
            return

        if debug:
            self.page_msg(
                "commit: current module '%s', current section '%s'" % (
                    self.module_name, self._current_section
                )
            )

        modified_sections = self._modified[self.module_id]
        for section in modified_sections:
            if debug: self.page_msg("modified section:", section)
            self._update()

    def _get_prepared_db_dict(self):
        """
        Daten sollen in die DB, egal ob update oder insert
        - Aktualisiert den _cache
        - picklet die Daten
        - Liefert das data-dict für den DB-Wrapper zurück
        """
        data = self._cache[self.module_id][self._current_section]
        data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        db_dict = {
            "pickled_data"      : data,
            "lastupdatetime"    : datetime.datetime.now(),
            "lastupdateby"      : self.session.get("user_id", None),
        }
        return db_dict

    def insert(self, data, section):
        """
        Neue Plugin-Daten in DB einfügen
        """
        self._current_section = section
        if not self.module_id in self._cache:
            self._cache[self.module_id] = {}
        self._cache[self.module_id][self._current_section] = data
        db_dict = self._get_prepared_db_dict()
        db_dict["plugin_id"] = self.module_id
        db_dict["section"] = self._current_section
        self.db.insert("plugin_cfg", db_dict)

    def _update(self):
        """
        Daten in DB aktualisieren
        """
        db_dict = self._get_prepared_db_dict()

        if debug: self.page_msg("updated in db:")
        self.db.update(
            table   = "plugin_cfg",
            data    = db_dict,
            where   = [
                ("plugin_id", self.module_id),
                ("section", self._current_section)
            ],
            debug = debug
        )
        if debug: self._get_from_db()

    #_________________________________________________________________________

    def delete_module_data(self, section="main"):
        """
        Wenn ein Modul deinstalliert wird, werden alle seine Daten gelöscht.
        """
        test = self.db.select(
            select_items    = ["plugin_id"],
            from_table      = "plugin_cfg",
            where           = ("plugin_id", self.module_id),
        )
        if test==[]:
            raise IndexError("Plugin has no plugin config data.")

        try:
            del(self._cache[self.module_id])
        except KeyError:
            pass

        self.db.delete(
            table   = "plugin_cfg",
            where   = ("plugin_id", self.module_id),
        )


class EntrieNotFound(Exception):
    """
    Eintrag ist nicht in der DB
    """
    pass