#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einstellungsdaten für Plugins/Module


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

#~ debug = True
debug = False

import datetime, copy

try:
    import cPickle as pickle
except ImportError:
    import pickle



class PluginConfig(dict):
    """
    Der cache dient nicht nur als Zwischenspeicher (bei fastCGI, mod_Python,
    sondern auch als Kontrolle in commit(). Damit wird getestet, ob die Daten
    auch wirklich geändert werden und in die DB geupdated werden müßen...
    """
    _cache = {}

    def __init__(self, request, response, read_db_data=True):
        self.request = request
        self.response = response

        # shorthands
        self.environ        = request.environ
        self.page_msg       = response.page_msg
        self.db             = request.db
        self.session        = request.session

        #~ self.page_msg(request.module_data)

        # Dict wird im Module-Manager an das request Objekt gehangen
        module_data = request.module_data

        self.module_id = int(module_data["id"]) # type long brauchen wir nicht ;)
        self.module_name = module_data["module_name"]
        self.method_name = module_data["method_name"]

        #~ if request.runlevel.is_install():
        if read_db_data:
            # plugin_cfg dict aus Cache/DB lesen
            self.init_dict()
        else:
            # Während der Installation oder beim installieren von neuen
            # Modulen/Plugins gibt es keine Daten in der DB.
            dict.__init__(self)

    def init_dict(self):
        #~ print self.module_id, self.module_name, self.method_name

        if self.module_id in self._cache:
            # Daten sind schon im cache
            if debug:
                self.page_msg("Used cached plugin_cfg!", self.__get_info())
            data = copy.deepcopy(self._cache[self.module_id])
            dict.__init__(self, data)
            return

        # Daten sind noch nicht im cache -> aus db holen
        data = self._get_db_data(self.module_id)
        data = self.unpickle_data(data)

        dict.__init__(self, data)
        self._cache[self.module_id] = copy.deepcopy(data)

        return True

    #_________________________________________________________________________

    def _get_db_data(self, module_id):
        data = self.db.select(
            select_items    = ["plugin_cfg"],
            from_table      = "plugins",
            where           = ("id", module_id),
        )
        try:
            data = data[0]["plugin_cfg"]
        except IndexError:
            raise NoConfigData

        if data == None:
            raise NoConfigData
            #~ return None # Das Plugin hat keine config Daten!

        data = data.tostring() # Aus der DB kommt ein array Objekt!
        if data == "":
            raise NoConfigData

        return data

    #_________________________________________________________________________

    def get_pickled_data(self, data):
        """
        Wird beim installieren mit dem module_admin gebraucht, sowie für
        das updaten per commit()
        """
        return pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    def unpickle_data(self, data):
        return pickle.loads(data)

    #_________________________________________________________________________
    # Daten in die DB updaten/einfügen

    def commit(self):
        assert not self._cache[self.module_id] is dict(self)

        if self._cache[self.module_id] == dict(self):
            if debug:
                self.page_msg(
                    "plugin_cfg.commit(): Data not changed!", self.__get_info()
                )
                self.page_msg(self._cache[self.module_id])
                self.page_msg(dict(self))
            return

        pickled_data = self.get_pickled_data(dict(self))

        if debug:
            self.page_msg(
                "plugin_cfg.commit(): Updated in db!", self.__get_info()
            )
        self.db.update(
            table   = "plugins",
            data    = {"plugin_cfg": pickled_data},
            where   = ("id", self.module_id),
        )

        # Cache aktualisieren, ein deepcopy wird immer bei init2 gemacht, wenn
        # Das Dict mit den cache Daten gefüllt werden ;)
        self._cache[self.module_id] = dict(self)

    def debug(self):
        self.page_msg("PluginConfig debug %s" % self.__get_info)
        self.page_msg(dict.__str__(self))

    #_________________________________________________________________________

    def __get_info(self):
        """
        Informationen für Fehler-/Debugmeldungen
        """
        return "(module: '%s.%s' id: %s)" % (
            self.module_name, self.method_name, self.module_id
        )



class PluginConfigError(Exception):
    pass

class NoConfigData(PluginConfigError):
    """
    Das Module/Plugin hat keine config Daten in der DB.
    """
    pass
