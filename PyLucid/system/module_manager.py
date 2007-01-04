#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

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

__version__= "$Rev$"


import sys, os, glob, imp, cgi, urllib

from PyLucid.system.exceptions import PyLucidException
from PyLucid.components import plugin_cfg


debug = False
#~ debug = True




class plugin_data:
    def __init__(self, request, response):
        self.request        = request

        # shorthands
        self.runlevel       = request.runlevel
        self.page_msg       = response.page_msg
        self.db             = request.db
        self.session        = request.session
        self.URLs           = request.URLs
        self.preferences    = request.preferences

        self.plugindata = {}

        # Daten der Installierten Module holen
        try:
            self.plugins = self.db.get_active_module_data()
        except Exception, e:
            msg = (
                "<strong>Can't get module data from DB</strong>: %s\n"
                "You must update PyLucid with install_PyLucid.py!"
            ) % e
            self.page_msg(msg)
            self.plugins = {}

        if debug:
            self.page_msg("Available Modules:",self.plugins.keys())

    def setup_module(self, module_name, method_name):
        self.module_name = module_name
        self.method_name = method_name

        try:
            self.module_id = self.plugins[module_name]["id"]
        except KeyError:
            msg = (
                "[Module/Plugin unknown or not installed/activated: %s]"
            ) % module_name
            raise PluginMethodUnknown(msg)

        if self.plugin_debug():
            self.page_msg("Plugin Debug for %s:" % module_name)

        if not module_name in self.plugindata:
            # Module neu
            self.plugindata[module_name] = {}

        if not method_name in self.plugindata[module_name]:
            # Die Methode ist noch unbekannt.
            try:
                method_properties = self.db.get_method_properties(
                    self.module_id, self.method_name
                )
            except IndexError:
                raise PluginMethodUnknown(
                    "[Method '%s' for Module '%s' unknown!]" % (
                        self.method_name, module_name
                    )
                )
            except Exception, e:
                msg = (
                    "Can't get method properties from DB: %s - "
                    "Did you init the basic modules with install_PyLucid???"
                ) % e
                raise RunModuleError(msg)

            self.plugindata[module_name][method_name] = method_properties

        self.package_name = self.plugins[module_name]["package_name"]

        self.current_properties = \
                        self.plugindata[self.module_name][self.method_name]

        if self.plugin_debug():
            self.page_msg("method_name:", self.method_name)


    def __getitem__(self, key):
        """
        Liefert die Method Properties zurück
        """
        return self.current_properties[key]

    def keys(self):
        return self.current_properties.keys()

    def plugin_debug(self):
        try:
            return self.plugins[self.module_name]["debug"]
        except KeyError,e:
            self.page_msg("KeyError in plugindata:", e)
            return False

    def setup_URLs(self):
        """
        URLs für Module vorbereiten
        """
        # FIXME
        self.oldCommandURL = self.URLs["command"]
        self.oldActionURL = self.URLs["action"]

        self.URLs.lock = False

        self.URLs["command"] = self.module_name
        self.URLs["action"] = self.method_name

        self.URLs.lock = True

        self.runlevel.save()
        self.runlevel.set_command()

    def restore_URLs(self):
        """
        Nach dem das Modul ausgeführt wurde,
        werden die alten URLs wiederhergestellt.
        """
        self.runlevel.restore()

        self.URLs.lock = False
        self.URLs["command"] = self.oldCommandURL
        self.URLs["action"] = self.oldActionURL
        self.URLs.lock = True

    def check_rights(self):
        """
        Überprüft ob der aktuelle User das Modul überhaupt ausführen darf.
        """
        try:
            must_login = self.current_properties["must_login"]
        except Exception, e:
            must_login = True
            self.page_msg(
                "must_login not defined (%s) in Module %s for method %s" % (
                    e, self.module_name, self.method_name
                )
            )

        if must_login == True:
            if self.session["user"] == False:
                raise RightsError(
                    "[You must login to use %s.%s]" % (
                        self.module_name, self.method_name
                    )
                )

            try:
                must_admin = self.current_properties["must_admin"]
            except Exception, e:
                must_admin = True
                self.page_msg(
                    "must_admin not defined (%s) in %s for method %s" % (
                        e, self.module_name, self.method_name
                    )
                )

            if (must_admin == True) and (self.session["isadmin"] == False):
                raise RightsError(
                    "You must be an admin to use method %s from module %s!" % (
                        self.method_name, self.module_name
                    )
                )

    def get_menu_data(self):
        """
        Liefert Daten für module_manager.build_menu()
        """
        result = {}
        for item in self.db.get_plugin_menu_data(self.module_id):
            if item["menu_section"] != None:
                if not item["menu_section"] in result:
                    result[item["menu_section"]] = []
                result[item["menu_section"]].append(item)
        return result

    #_________________________________________________________________________

    def debug_data(self):
        self.page_msg(" -"*40)
        self.page_msg("Debug module_manager.plugin_data:")
        self.page_msg("self.plugins:")
        for k,v in self.plugins.iteritems():
            self.page_msg("%s: %s" % (k,v))
        self.page_msg(" -"*40)
        self.page_msg("self.plugindata:", self.plugindata)
        #~ for k,v in self.cache.iteritems():
            #~ self.page_msg(k,v)










class module_manager:
    def __init__(self):
        # Alle Angaben werden bei run_tag oder run_function ausgefüllt...
        self.module_name    = "undefined"
        self.method_name    = "undefined"

    def init2(self, request, response):
        self.request        = request
        self.response       = response

        # shorthands
        self.environ        = request.environ
        self.staticTags     = request.staticTags
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.log            = request.log
        self.module_manager = request.module_manager
        self.tools          = request.tools
        self.render         = request.render
        self.templates      = request.templates

        self.page_msg       = response.page_msg

        self.plugin_data = plugin_data(request, response)

        self.isadmin = self.session.get("isadmin", False)
        if self.preferences["ModuleManager_error_handling"] == False or \
                                                        self.isadmin == True:
            # Fehler führen zu einem CGI-Traceback
            self.error_handling = False
        else:
            # Fehler werden in einem Satz zusammen gefasst
            self.error_handling = True

    #_________________________________________________________________________

    def run_tag(self, tag):
        """
        Ausführen von:
        <lucidTag:'tag'/>
        """

        if tag in self.staticTags:
            return self.staticTags[tag]

        if tag.find(".") != -1:
            self.module_name, self.method_name = tag.split(".",1)
        else:
            self.module_name = tag
            self.method_name = "lucidTag"

        return self._run_module_method(function_info={})


    def run_function( self, function_name, function_info ):
        """
        Ausführen von:
        <lucidFunction:'function_name'>'function_info'</lucidFunction>
        """
        self.module_name = function_name
        self.method_name = "lucidFunction"

        #~ if debug:
        #~ self.page_msg(
            #~ "function_name:", function_name, "function_info:", function_info
        #~ )

        function_info = {"function_info": function_info}
        return self._run_module_method(function_info)


    def run_command(self):
        """
        ein Kommando ausführen.
        """
        pathInfo = self.environ["PATH_INFO"].split("&")[0]
        pathInfo = pathInfo.strip("/")
        pathInfo = pathInfo.split("/")[1:]

        try:
            self.module_name = pathInfo[1]
            self.method_name = pathInfo[2]
        except IndexError:
            self.page_msg("Wrong command path!")
            return

        function_info = pathInfo[3:]

        if function_info == []:
            function_info = {}
        else:
            function_info = {"function_info": function_info}

        self.request.staticTags["page_title"] = "%s.%s" % (
            self.module_name, self.method_name
        )

        return self._run_module_method(function_info)


    #_________________________________________________________________________

    def _run_module_method(self, function_info={}):
        """
        Führt eine Methode eines Module aus.
        Kommt es irgendwo zu einem Fehler, ist es die selbsterstellte
        "RunModuleError"-Exception mit einer passenden Fehlermeldung.
        """
        #~ if debug: self.page_msg("function_info:", function_info)
        try:
            self.plugin_data.setup_module(self.module_name, self.method_name)
        except PluginMethodUnknown, e:
            # Fehler nur anzeigen
            msg = "run %s.%s, error '%s'" % (
                self.module_name, self.method_name,e
            )
            self.page_msg(msg)
            return msg
        except RunModuleError, e:
            msg = "[setup module '%s.%s' unknown Error: %s]" % (
                self.module_name, self.method_name, e
            )
            if self.error_handling == False:
                # Traceback erzeugen
                raise RunModuleError(msg)
            else:
                # Fehler nur anzeigen
                self.page_msg(msg)
                return str(msg)

        #~ self.page_msg(self.module_name, self.method_name, self.plugin_data.keys())

        try:
            self.plugin_data.check_rights()
        except RightsError, e:
            if self.plugin_data["no_rights_error"] == 1:
                # Rechte Fehler sollen nicht angezeigt werden
                return ""
            else:
                self.page_msg(e)
                return ""

        self.plugin_data.setup_URLs()

        try:
            moduleOutput = self._run_method(function_info)
        except RunModuleError, e:
            self.page_msg(e)
            moduleOutput = ""

        self.plugin_data.restore_URLs()

        return moduleOutput


    def _run_with_error_handling(self, unbound_method, function_info):
        if self.plugin_data.plugin_debug == True:
            self.page_msg(
                "function_info for method '%s': %s" % (
                    self.method_name, function_info
                )
            )
        try:
            # Dict-Argumente übergeben
            return unbound_method(**function_info)
        except SystemExit:
            # Module dürfen zum Debugging auch einen sysexit machen...
            pass
        except TypeError, e:
            if not str(e).startswith(unbound_method.__name__):
                # Der Fehler ist nicht hier, bei der Dict übergabe zur
                # unbound_method() aufgetretten, sondern irgendwo im
                # Modul selber!
                raise # Vollen Traceback ausführen

            # Ermitteln der Argumente die wirklich von der unbound_method()
            # verlangt werden
            import inspect
            args = inspect.getargspec(unbound_method)
            real_function_info = args[0][1:]
            real_function_info.sort()
            argcount = len(real_function_info)

            msg = "ModuleManager 'function_info' error: "
            msg += "%s() takes exactly %s arguments %s, " % (
                unbound_method.__name__, argcount, real_function_info
            )
            msg += "and I have %s given the dict: %s " % (
                len(function_info), function_info
            )

            raise RunModuleError(msg)


    def _run_method(self, function_info):
        """
        Startet die Methode und verarbeitet die Ausgaben
        """
        def run_error(msg):
            msg = "[Can't run '%s.%s': %s]" % (
                self.module_name, self.method_name, msg
            )
            if self.error_handling == True:
                # Fehler nur anzeigen
                raise RunModuleError(msg) # Wird später abgefangen
            else:
                # Traceback erzeugen
                raise Exception(msg)


        module_class = self._get_module_class()
        local_request_obj = self._get_local_request_obj()
        class_instance = self._get_class_instance(
            local_request_obj, module_class
        )
        unbound_method = self._get_unbound_method(class_instance)

        # Methode "ausführen"
        if self.error_handling == True: # Fehler nur anzeigen
            try:
                output = self._run_with_error_handling(
                    unbound_method, function_info
                )
            except KeyError, e:
                run_error("KeyError: %s" % e)
            except PyLucidException, e:
                # Interne Fehlerseite wurde geforfen, aber Fehler sollen
                # als Satz zusammen gefasst werden.
                # Bei config.ModuleManager_error_handling = True
                raise RunModuleError(e.get_error_page_msg())
            except Exception, e:
                run_error(e)
        else:
            output = self._run_with_error_handling(
                unbound_method, function_info
            )

        # plugin_cfg evtl. speichern
        local_request_obj.plugin_cfg.commit()

        return output

    #_________________________________________________________________________

    def _get_module_class(self):
        """
        Importiert das Modul und liefert die Klasse als Objekt zurück
        Nutzt dazu:
            - self.module_name
            - self.plugin_data.package_name
        """
        if self.plugin_data.plugin_debug():
            msg = (
                "Import module mit error handling: %s"
            ) % self.preferences["ModuleManager_error_handling"]
            self.page_msg(msg)

        def _import(package_name, module_name):
            return __import__(
                "%s.%s" % (package_name, module_name), {}, {}, [module_name]
            )

        if self.preferences["ModuleManager_error_handling"] == False:
            import_object = _import(
                self.plugin_data.package_name, self.module_name
            )

        try:
            import_object = _import(
                self.plugin_data.package_name, self.module_name
            )
        except Exception, e:
            raise RunModuleError(
                "[Can't import Modul '%s': %s]" % (self.module_name, e)
            )

        try:
            return getattr(import_object, self.module_name)
        except Exception, e:
            raise RunModuleError(
                "[Can't get class '%s' from module '%s': %s]" % (
                    self.module_name, self.module_name, e
                )
            )

    def _get_class_instance(self, request_obj, module_class):
        """
        Instanziert die Module/Plugin Klasse und liefert diese zurück
        """
        if self.error_handling == True:
            # Fehler nur anzeigen
            try:
                class_instance = module_class(request_obj, self.response)
            except Exception, e:
                raise RunModuleError(
                    "[Can't make class intance from module '%s': %s]" % (
                        self.module_name, e
                    )
                )
        else:
            # Traceback erzeugen
            try:
                class_instance = module_class(request_obj, self.response)
            except TypeError, e:
                msg = (
                    "TypeError, module '%s.%s': %s"
                    " --- module-class must received: (request, response) !"
                ) % (self.module_name, self.method_name, e)
                raise TypeError(msg)

        return class_instance

    def _get_unbound_method(self, class_instance):
        """
        Holt die zu startende Methode aus der Modul/Plugin-Klasse herraus,
        liefert diese als 'unbound method' zurück.
        """
        ##____________________________________________________________________
        ## Methode per getattr holen
        if self.error_handling == True: # Fehler nur anzeigen
            try:
                unbound_method = getattr(
                    class_instance, self.plugin_data.method_name
                )
            except Exception, e:
                raise RunModuleError(
                    "[Can't get method '%s' from module '%s': %s]" % (
                        self.plugin_data.method_name, self.module_name, e
                    )
                )
        else:
            unbound_method = getattr(
                class_instance, self.plugin_data.method_name
            )

        return unbound_method


    #_________________________________________________________________________
    def _get_local_request_obj(self):
        """
        Fügt das plugin_cfg an das request Objekt, mit den Daten für das
        aktuelle Plugin.
        """
        plugin_cfg_obj = plugin_cfg.get_plugin_cfg_obj(
            self.request, self.response,
            self.plugin_data.module_id,
            self.plugin_data.module_name,
            self.plugin_data.method_name
        )

        local_request_obj = self.request
        local_request_obj.plugin_cfg = plugin_cfg_obj

        return local_request_obj

    #_________________________________________________________________________
    # Zusatz Methoden für die Module selber

    def build_menu(self):
        result = ""
        if debug:
            result += "module_manager.build_menu():"
            result += self.plugin_data.package_name
            result += self.module_name
            result += "self.plugin_data:", self.plugin_data.debug_data()

        menu_data = self.plugin_data.get_menu_data()
        result += '<ul class="module_manager_menu">'
        for menu_section, section_data in menu_data.iteritems():
            result += "<li><h5>%s</h5><ul>" % menu_section
            for item in section_data:
                result += '<li><a href="%s">%s</a></li>' % (
                    self.URLs.commandLink(self.module_name, item["method_name"]),
                    item["menu_description"]
                )
            result += "</ul>"
        result += "</ul>"

        return result

    #_________________________________________________________________________
    # page_msg debug

    def debug(self):
        self.page_msg("Module Manager debug:")
        self.page_msg(self.plugin_data.debug_data())


class ModuleManagerError(Exception):
    pass

class RunModuleError(ModuleManagerError):
    pass

class PluginMethodUnknown(ModuleManagerError):
    """
    Das Module/Plugin oder die Methode ist unbekannt, steht nicht in der DB
    """
    pass

class RightsError(ModuleManagerError):
    """
    Ausführungsrechte Stimmen nicht
    """
    pass
















