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

import datetime, copy

try:
    import cPickle as pickle
except ImportError:
    import pickle


class NoPluginConfig(object):
    """
    Hat ein Module/Plugin keine plugin config definiert, wird diese Klasse an
    das lokale request-Objekt dran gehangen.
    So werden brauchbare Fehlermeldungen erzeugt, wenn das Plugin dennoch auf
    die nicht existierende config zugreifen möchte ;)
    """
    def __init__(self, module_name):
        self.module_name = module_name

    def __getattr__(self, name):
        self._error()

    def __contains__(self, key): self._error()
    def __str__(self): self._error()
    def __setitem__(self, key, item): self._error()

    def commit(self):
        # Der Module-Manager ruft immer commit auf ;)
        pass

    def _error(self):
        try:
            import inspect
            for stack_frame in inspect.stack():
                # Im stack vorwärts gehen, bis außerhalb dieser Datei
                filename = stack_frame[1]
                lineno = stack_frame[2]
                #~ print filename, __file__
                if filename != __file__:
                    break

            filename = "...%s" % filename[-25:]
            fileinfo = "%-25s line %3s: " % (filename, lineno)
        except Exception, e:
            fileinfo = "(inspect Error: %s)" % e

        msg = (
            "Error: Plugin/Module '%s' has no plugin-config!"
            " But in %s you access to the plugin_cfg object ;)"
            " If you would like to use plugin_cfg, you must setup your"
            " module/plugin config file!"
        ) % (self.module_name, fileinfo)
        raise AttributeError(msg)



class PluginConfig(dict):
    """
    Der cache dient nicht nur als Zwischenspeicher (bei fastCGI, mod_Python,
    sondern auch als Kontrolle in commit(). Damit wird getestet, ob die Daten
    auch wirklich geändert werden und in die DB geupdated werden müßen...
    """
    _cache = {}

    def __init__(self, request, response, module_id, module_name, method_name):
        self.request = request
        self.response = response

        # shorthands
        self.environ        = request.environ
        self.page_msg       = response.page_msg
        self.db             = request.db
        self.session        = request.session

        self.module_id = int(module_id) # type long brauchen wir nicht ;)
        self.module_name = module_name
        self.method_name = method_name

    def init2(self):
        if self.module_id in self._cache:
            # Daten sind schon im cache
            if debug:
                self.page_msg("Used cached plugin_cfg!", self.__get_info())
            data = copy.deepcopy(self._cache[self.module_id])
            dict.__init__(self, data)
            return

        # Daten sind noch nicht im cache -> aus db holen
        data = self._get_db_data(self.module_id)
        if data == "":
            # Das Modul/Plugin hat keine config
            if debug:
                self.page_msg("Plugin has no config. %s" % self.__get_info())
            return False

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
        )[0]["plugin_cfg"]
        data = data.tostring() # Aus der DB kommt ein array Objekt!
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

    #_________________________________________________________________________



def get_plugin_cfg_obj(request, response, module_id, module_name, method_name):
    plugin_cfg_obj = PluginConfig(
        request, response, module_id, module_name, method_name
    )
    has_config = plugin_cfg_obj.init2()
    if has_config == False:
        # Das aktuelle Plugin hat keine Config
        return NoPluginConfig(module_name)
    else:
        return plugin_cfg_obj



#~ class PluginConfigError(Exception):
    #~ pass

#~ class EntrieNotFound(PluginConfigError):
    #~ """
    #~ Eintrag ist nicht in der DB
    #~ """
    #~ pass

#~ class DuplicateEntrie(PluginConfigError):
    #~ """
    #~ Eintrag soll in DB eingefügt werden, existiert aber schon
    #~ """
    #~ pass