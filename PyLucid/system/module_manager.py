#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

# by jensdiemer.de (steht unter GPL-License)
"""

__version__="0.3.1"

__history__="""
v0.3.1
    - New error handling: "Wrong command path"
v0.3
    - Anpassung an colubrid 1.0
    - Funktion "CGI_dependency Methoden" rausgeschmissen
v0.2.6
    - Andere Fehlerbehandlung, wenn noch nicht von v0.5 geupdated wurde bzw.
        wenn die Plugin-Tabellen noch nicht (in der neuen Form) existieren.
v0.2.5
    - ModuleManager_error_handling auch bei _get_module()
v0.2.4
    - ModuleManager_error_handling wird auch bei _make_class_instance()
        beachtet. Damit Fehler im Module's __init__ auch als echter
        Traceback zu sehen ist
v0.2.3
    - Anderer Aufruf des Module, wenn
        config.system.ModuleManager_error_handling damit Traceback
        Aussagekräftiger ist.
v0.2.2
    - Bessere Fehlerausgabe bei einem Fehler in der
        lucidFunction-Parameterübergabe
v0.2.1
    - NEU: ModulManager config "sys_exit": Damit ein Modul auch wirklich einen
        sys.exit() ausführen kann.
v0.2
    - NEU: ModulManager config "get_CGI_data": Zur direkten Übergabe von
        CGI-Daten an die gestartete Methode.
    - Bessere Fehlerausgabe bei _run_method() und _make_class_instance()
v0.1.3
    - Die Regel "must_login" wird nun anhand von self.session.has_key("user")
        ermittelt
v0.1.2
    - Ein paar mehr debug Ausgaben
    - CGI_dependency Methoden können nun anderen Einstellungen ("direct_out",
        "apply_markup" usw.) haben, diese werden nun berücksichtigt
v0.1.1
    - Module können nun auch Seiten produzieren, die noch durch einen Parser
        laufen sollen.
v0.1.0
    - Komplett neu Programmiert!
v0.0.8
    - Andere Handhabung von Modul-Ausgaben auf stderr. Diese sehen nur
        eingeloggte User als page_msg.
v0.0.7
    - NEU: Module können nun auch nur normale print Ausgaben machen, die dann
        in die Seite "eingeblendet" werden sollen
    - NEU: "direct_out"-Parameter, wird z.B. für das schreiben des Cookies in
        user_auth.py verwendet. Dann werden print-Ausgaben nicht
        zwischengespeichert.
v0.0.6
    - Fehler beim import sehen nur Admins
v0.0.5
    - Debug mit page_msg
v0.0.4
    - "must_login" und "must_admin" muß nun in jedem Modul definiert worden sein.
    - Fehlerabfrage beim Module/Aktion starten
v0.0.3
    - NEU: start_module()
v0.0.2
    - Großer Umbau :)
v0.0.1
    - erste Version
"""


#~ import cgitb;cgitb.enable()
import sys, os, glob, imp, cgi, urllib

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n" # Hardcore-Debugging ;)

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
            self.page_msg("<strong>Can't get module data from DB</strong>: %s" % e)
            self.page_msg("You must update PyLucid with install_PyLucid.py!")
            self.plugins = {}

        # Fast Patch to new Filesystem (v0.7)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for k,v in self.plugins.iteritems():
            v['package_name'] = v['package_name'].replace("PyLucid_", "PyLucid.")
            v['package_name'] = v['package_name'].replace("PyLucid/", "PyLucid.")
            #~ self.page_msg(k,v)

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
            #~ if self.runlevel.is_normal():
                #~ msg = "<!-- %s -->" % msg

            raise run_module_error(msg)

        if self.plugin_debug():
            self.page_msg("Plugin Debug for %s:" % module_name)

        if not self.plugindata.has_key(module_name):
            # Module neu
            self.plugindata[module_name] = {}

        if not self.plugindata[module_name].has_key(method_name):
            # Die Methode ist noch unbekannt.
            try:
                method_properties = self.db.get_method_properties(
                    self.module_id, self.method_name
                )
            except IndexError:
                raise run_module_error(
                    "[Method '%s' for Module '%s' unknown!]" % (
                        self.method_name, module_name
                    )
                )
            except Exception, e:
                raise Exception(
                    "Can't get method properties from DB: %s - "
                    "Did you init the basic modules with install_PyLucid???" % e
                )

            self.plugindata[module_name][method_name] = method_properties

        self.package_name = self.plugins[module_name]["package_name"]

        self.current_properties = self.plugindata[self.module_name][self.method_name]

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
                raise rights_error(
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
                raise rights_error(
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
                if not result.has_key(item["menu_section"]):
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


    def run_tag(self, tag):
        """
        Ausführen von:
        <lucidTag:'tag'/>
        """
        if self.staticTags.has_key(tag):
            return self.staticTags[tag]

        if tag.find(".") != -1:
            self.module_name, self.method_name = tag.split(".",1)
        else:
            self.module_name = tag
            self.method_name = "lucidTag"

        try:
            return self._run_module_method()
        except run_module_error, e:
            pass
        except rights_error, e:
            if self.plugin_data["no_rights_error"] == 1:
                return ""

        self.page_msg("run tag %s, error '%s'" % (tag,e))
        return str(e)

    def run_function( self, function_name, function_info ):
        """
        Ausführen von:
        <lucidFunction:'function_name'>'function_info'</lucidFunction>
        """
        self.module_name = function_name
        self.method_name = "lucidFunction"

        #~ if debug: self.page_msg("function_name:", function_name, "function_info:", function_info)

        function_info = {"function_info": function_info}
        try:
            return self._run_module_method(function_info)
        except run_module_error, e:
            self.page_msg(e)
        except rights_error, e:
            if self.plugin_data["no_rights_error"] == 1:
                return ""
            self.page_msg(e)

    def run_command(self):
        """
        ein Kommando ausführen.
        """
        pathInfo = self.environ["PATH_INFO"].split("&")[0]
        pathInfo = pathInfo.strip("/")
        pathInfo = pathInfo.split("/")[1:]

        try:
            self.module_name = pathInfo[0]
            self.method_name = pathInfo[1]
        except IndexError:
            self.page_msg("Wrong command path!")
            return

        function_info = pathInfo[2:]

        if function_info == []:
            function_info = {}
        else:
            function_info = {"function_info": function_info}

        self.request.staticTags["page_title"] = "%s.%s" % (
            self.module_name, self.method_name
        )

        try:
            moduleOutput = self._run_module_method(function_info)
        except run_module_error, e:
            pass
        except rights_error, e:
            if self.plugin_data["no_rights_error"] == 1:
                return ""
        else:
            return moduleOutput

        self.page_msg(e)
        return str(e)

    def _run_module_method(self, method_arguments={}):
        """
        Führt eine Methode eines Module aus.
        Kommt es irgendwo zu einem Fehler, ist es die selbsterstellte
        "run_module_error"-Exception mit einer passenden Fehlermeldung.
        """
        #~ if debug: self.page_msg("method_arguments:", method_arguments)
        #~ try:
        self.plugin_data.setup_module(self.module_name, self.method_name)
        #~ except KeyError:
            #~ raise run_module_error(
                #~ "[module name '%s' unknown (method: %s)]" % (self.module_name, self.method_name)
            #~ )

        #~ self.page_msg(self.module_name, self.method_name, self.plugin_data.keys())

        self.plugin_data.check_rights()

        module_class = self._get_module_class()

        self.plugin_data.setup_URLs()

        moduleOutput = self._run_method(module_class, method_arguments)

        self.plugin_data.restore_URLs()

        return moduleOutput


    def _get_module_class(self):
        """
        Importiert das Module und packt die Klasse als Objekt in self.data
        """
        def _import(package_name, module_name):
            return __import__(
                "%s.%s" % (package_name, module_name), {}, {}, [module_name]
            )

        if self.plugin_data.plugin_debug():
            msg = (
                "Import module mit error handling: %s"
            ) % self.preferences["ModuleManager_error_handling"]
            self.page_msg(msg)

        module_name = self.module_name
        package_name = self.plugin_data.package_name

        if self.preferences["ModuleManager_error_handling"] == False:
            import_object = _import(package_name, module_name)

        try:
            import_object = _import(package_name, module_name)
        except Exception, e:
            raise run_module_error(
                "[Can't import Modul '%s': %s]" % ( self.module_name, e )
            )

        try:
            return getattr(import_object, self.module_name)
        except Exception, e:
            raise run_module_error(
                "[Can't get class '%s' from module '%s': %s]" % (
                    self.module_name, self.module_name, e
                )
            )


    def _run_with_error_handling(self, unbound_method, method_arguments):
        if self.plugin_data.plugin_debug == True:
            self.page_msg(
                "method_arguments for method '%s': %s" % (
                    self.method_name, method_arguments
                )
            )
        try:
            # Dict-Argumente übergeben
            return unbound_method(**method_arguments)
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
            real_method_arguments = args[0][1:]
            real_method_arguments.sort()
            argcount = len(real_method_arguments)

            msg = "ModuleManager 'method_arguments' error: "
            msg += "%s() takes exactly %s arguments %s, " % (
                unbound_method.__name__, argcount, real_method_arguments
            )
            msg += "and I have %s given the dict: %s " % (
                len(method_arguments), method_arguments
            )

            raise run_module_error(msg)


    def _run_method(self, module_class, method_arguments={}):
        """
        Startet die Methode und verarbeitet die Ausgaben
        """
        #~ self.page_msg(
            #~ "method_arguments:", method_arguments,
            #~ "---", self.module_name, self.method_name
        #~ )

        #~ if debug: self.page_msg("method_arguments:", method_arguments)
        def run_error(msg):
            msg = "[Can't run '%s.%s': %s]" % (
                self.module_name, self.method_name, msg
            )

            if self.preferences["ModuleManager_error_handling"] == True:
                raise run_module_error(msg)
            else:
                raise Exception(msg)


        #~ if self.plugin_data["direct_out"] == True:
            #~ # Direktes schreiben in das globale response Objekt
            #~ responseObject = self.response
        #~ else:
        # Das Modul schreibt in einem lokalen Puffer, um die Ausgaben in
        # die CMS Seite einbauen zu können
        #~ old_responseObject = self.response
        #~ self.response = self.tools.out_buffer()

        # Instanz erstellen und PyLucid-Objekte übergeben
        if self.preferences["ModuleManager_error_handling"] == True:
            try:
                class_instance = module_class(self.request, self.response)
            except Exception, e:
                raise run_module_error(
                    "[Can't make class intance from module '%s': %s]" % (
                        self.module_name, e
                    )
                )
        else:
            try:
                class_instance = module_class(self.request, self.response)
            except TypeError, e:
                msg = (
                    "TypeError, module '%s.%s': %s"
                    " --- module-class must received: (request, response) !"
                ) % (self.module_name, self.method_name, e)
                raise TypeError(msg)

        # Methode aus Klasse erhalten
        if self.preferences["ModuleManager_error_handling"] == True:
            try:
                unbound_method = getattr(
                    class_instance, self.plugin_data.method_name
                )
            except Exception, e:
                raise run_module_error(
                    "[Can't get method '%s' from module '%s': %s]" % (
                        self.plugin_data.method_name, self.module_name, e
                    )
                )
        else:
            unbound_method = getattr(
                class_instance, self.plugin_data.method_name
            )

        # Methode "ausführen"
        if self.preferences["ModuleManager_error_handling"] == False:
            moduleOutput = self._run_with_error_handling(
                unbound_method, method_arguments
            )
        else:
            try:
                moduleOutput = self._run_with_error_handling(
                    unbound_method, method_arguments
                )
            except KeyError, e:
                run_error("KeyError: %s" % e)
            except Exception, e:
                run_error(e)

        return moduleOutput


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

class run_module_error(Exception):
    pass

class rights_error(Exception):
    """
    Ausführungsrechte Stimmen nicht
    """
    pass
















