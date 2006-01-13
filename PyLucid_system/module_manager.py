#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

# by jensdiemer.de (steht unter GPL-License)


"""

__version__="0.2.6"

__history__="""
v0.2.6
    - Andere Fehlerbehandlung, wenn noch nicht von v0.5 geupdated wurde bzw. wenn die Plugin-Tabellen
        noch nicht (in der neuen Form) existieren.
v0.2.5
    - ModuleManager_error_handling auch bei _get_module()
v0.2.4
    - ModuleManager_error_handling wird auch bei _make_class_instance() beachtet. Damit Fehler im
        Module's __init__ auch als echter Traceback zu sehen ist
v0.2.3
    - Anderer Aufruf des Module, wenn config.system.ModuleManager_error_handling damit Traceback
        Aussagekräftiger ist.
v0.2.2
    - Bessere Fehlerausgabe bei einem Fehler in der lucidFunction-Parameterübergabe
v0.2.1
    - NEU: ModulManager config "sys_exit": Damit ein Modul auch wirklich einen sys.exit() ausführen kann.
v0.2
    - NEU: ModulManager config "get_CGI_data": Zur direkten Übergabe von CGI-Daten an die
        gestartete Methode.
    - Bessere Fehlerausgabe bei _run_method() und _make_class_instance()
v0.1.3
    - Die Regel "must_login" wird nun anhand von self.session.has_key("user") ermittelt
v0.1.2
    - Ein paar mehr debug Ausgaben
    - CGI_dependency Methoden können nun anderen Einstellungen ("direct_out", "apply_markup" usw.) haben,
        diese werden nun berücksichtigt
v0.1.1
    - Module können nun auch Seiten produzieren, die noch durch einen Parser laufen sollen.
v0.1.0
    - Komplett neu Programmiert!
v0.0.8
    - Andere Handhabung von Modul-Ausgaben auf stderr. Diese sehen nur eingeloggte User als
        page_msg.
v0.0.7
    - NEU: Module können nun auch nur normale print Ausgaben machen, die dann in die
        Seite "eingeblendet" werden sollen
    - NEU: "direct_out"-Parameter, wird z.B. für das schreiben des Cookies in user_auth.py
        verwendet. Dann werden print-Ausgaben nicht zwischengespeichert.
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
    def __init__(self, PyLucid):
        self.CGIdata    = PyLucid["CGIdata"]
        self.db         = PyLucid["db"]
        self.session    = PyLucid["session"]
        self.page_msg   = PyLucid["page_msg"]
        self.URLs       = PyLucid["URLs"]

        self.plugindata = {}

        # Daten der Installierten Module holen
        try:
            self.plugins = self.db.get_active_module_data()
        except Exception, e:
            self.page_msg("<strong>Can't get module data from DB</strong>: %s" % e)
            self.page_msg("You must update PyLucid with install_PyLucid.py!")
            self.plugins = {}

        if debug:
            self.page_msg("Available Modules:",self.plugins.keys())

    def setup_module(self, module_name, main_method):
        self.module_name = module_name
        self.main_method = main_method
        try:
            self.module_id = self.plugins[module_name]["id"]
        except KeyError:
            raise run_module_error("[Module/Plugin unknown or not installed/activated: %s]" % module_name)

        if self.plugin_debug():
            self.page_msg("Plugin Debug for %s:" % module_name)

        if not self.plugindata.has_key(module_name):
            # Module neu
            self.plugindata[module_name] = {}

        if not self.plugindata[module_name].has_key(main_method):
            # Die Methode ist noch unbekannt.
            try:
                method_properties, CGI_dependent_data = self.db.get_method_properties(self.module_id, self.main_method)
            except IndexError:
                raise run_module_error("[Method '%s' for Module '%s' unknown!]" % (self.main_method, module_name))
            except Exception, e:
                raise Exception(
                    "Can't get method properties from DB: %s - "
                    "Did you init the basic modules with install_PyLucid???" % e
                )

            self.plugindata[module_name][main_method] = method_properties
            self.plugindata[module_name][main_method]["CGI_dependent_data"] = CGI_dependent_data

        self.package_name = self.plugins[module_name]["package_name"]

        self.current_properties = self.plugindata[self.module_name][self.main_method]

        self.check_CGI_dependent()
        self.setup_get_CGI_data()

        if self.plugin_debug():
            self.page_msg("current_method:", self.current_method)

    def check_CGI_dependent(self):
        """
        Ändert die self.current_method abhängig von den CGI_dependent-Angaben und
        den tatsälich vorhandenen CGIdaten
        """
        self.current_method = self.main_method

        if self.plugin_debug(): self.CGIdata.debug()

        if not self.current_properties["CGI_dependent_data"]:
            # Es gibt keine CGI-Abhängigkeiten
            if self.plugin_debug():
                self.page_msg("There is no CGI dependent data for %s.%s" % (self.module_name,self.main_method))
            return

        for dependent_data in self.current_properties["CGI_dependent_data"]:
            if self.plugin_debug(): self.page_msg("dependent_data:",cgi.escape(str(dependent_data)))
            for k,v in dependent_data["CGI_laws"].iteritems():
                if self.CGIdata.has_key(k) and self.CGIdata[k] == v:
                    self.current_method = dependent_data["method_name"]
                    self.current_properties.update(dependent_data)
                    return
            if self.plugin_debug(): self.page_msg("no method change in CGIdata!")

    def setup_get_CGI_data(self):
        """
        Bereitet die CGI-Daten bei "get_CGI_data" vor, indem die Daten
        in den verlangten Typ gewandert wird.
        """
        self.get_CGI_data = {}
        if not self.current_properties.has_key("get_CGI_data") or \
            self.current_properties["get_CGI_data"] == None:
            return

        for k,type_obj in self.current_properties["get_CGI_data"].iteritems():
            if not self.CGIdata.has_key(k):
                continue

            # CGI-Daten in den angebenen Type konvertieren
            try:
                self.get_CGI_data[k] = type_obj(self.CGIdata[k])
            except Exception, e:
                self.page_msg(
                    "Error: Can't convert CGIdata Type from %s to %s (%s)" % (
                        cgi.escape(self.CGIdata[k]), cgi.escape(str(type_obj)), self.current_method
                    )
                )
        if debug:
            self.page_msg("setup_get_CGI_data()-Debug for %s: %s" % (self.current_method, self.get_CGI_data))

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
        self.URLs["command"]        = "%s&command=%s" % (self.URLs["base"], self.module_name)
        self.URLs["action"]         = "%s&command=%s&action=" % (self.URLs["base"], self.module_name)
        self.URLs["main_action"]    = self.URLs["action"] + self.main_method
        self.URLs["current_action"] = self.URLs["action"] + self.current_method

    def check_rights(self):
        """
        Überprüft ob der aktuelle User das Modul überhaupt ausführen darf.
        """
        try:
            must_login = self.current_properties["must_login"]
        except Exception, e:
            must_login = True
            self.page_msg(
                "must_login not defined (%s) in Module %s for method %s" % (e, self.module_name, self.current_method)
            )

        if must_login == True:
            if self.session["user"] == False:
                #~ raise run_module_error(
                    #~ "[You must login to use %s for method %s]" % (self.module_name, method)
                #~ )
                raise rights_error(
                    "[You must login to use %s.%s]" % (self.module_name, self.current_method)
                )

            try:
                must_admin = self.current_properties["must_admin"]
            except Exception, e:
                must_admin = True
                self.page_msg(
                    "must_admin not defined (%s) in %s for method %s" % (e, self.module_name, method)
                )

            if (must_admin == True) and (self.session["isadmin"] == False):
                raise rights_error(
                    "You must be an admin to use method %s from module %s!" % (method, self.module_name)
                )

    def get_menu_data(self):
        """
        Liefert Daten für module_manager.build_menu()
        """
        result = {}
        for item in self.db.get_plugin_menu_data(self.module_id):
            if item["parent_method_id"] == None and item["menu_section"] != None:
                if not result.has_key(item["menu_section"]):
                    result[item["menu_section"]] = []
                result[item["menu_section"]].append(item)
        return result

    #________________________________________________________________________________________

    def debug_data(self):
        self.page_msg(" -"*40)
        self.page_msg("Debug module_manager.plugin_data:")
        self.page_msg(self.plugins)
        self.page_msg(self.plugindata)
        #~ for k,v in self.cache.iteritems():
            #~ self.page_msg(k,v)
        self.page_msg(" -"*40)









class module_manager:
    def __init__( self, PyLucid ):
        self.PyLucid        = PyLucid
        self.db             = PyLucid["db"]
        self.page_msg       = PyLucid["page_msg"]
        self.session        = PyLucid["session"]
        self.CGIdata        = PyLucid["CGIdata"]
        self.tools          = PyLucid["tools"]
        self.config         = PyLucid["config"]
        self.parser         = PyLucid["parser"]
        self.render         = PyLucid["render"]
        self.URLs           = PyLucid["URLs"]

        self.plugin_data = plugin_data(PyLucid)

        # Alle Angaben werden bei run_tag oder run_function ausgefüllt...
        self.module_name    = "undefined"
        self.main_method    = "undefined"
        self.current_method = "undefined"

    def run_tag( self, tag ):
        """
        Ausführen von:
        <lucidTag:'tag'/>
        """
        if tag.find(".") != -1:
            self.module_name, self.main_method = tag.split(".",1)
        else:
            self.module_name = tag
            self.main_method = "lucidTag"
            self.current_method = "lucidTag"

        try:
            return self._run_module_method()
        except run_module_error, e:
            pass
        except rights_error, e:
            if self.plugin_data["no_rights_error"] == 1:
                return ""

        self.page_msg( "run tag %s, error '%s'" % (tag,e) )
        return str(e)

    def run_function( self, function_name, function_info ):
        """
        Ausführen von:
        <lucidFunction:'function_name'>'function_info'</lucidFunction>
        """
        self.module_name    = function_name
        self.main_method    = "lucidFunction"
        self.current_method = "lucidFunction"

        #~ if debug: self.page_msg("function_name:", function_name, "function_info:", function_info)

        function_info = {"function_info": function_info}
        try:
            return self._run_module_method(function_info)
        except run_module_error, e:
            pass
        except rights_error, e:
            if self.plugin_data.get_properties()["no_rights_error"] == 1:
                return ""

        self.page_msg(e)
        return str(e)

    def run_command( self ):
        """
        ein Kommando ausführen.
        """
        try:
            self.module_name = self.CGIdata["command"]
            self.main_method = self.CGIdata["action"]
        except KeyError, e:
            self.page_msg( "Error in command: KeyError", e )
            return

        if debug == True: self.page_msg( "Command: %s; action: %s" % (self.module_name, self.main_method) )

        try:
            return self._run_module_method()
        except run_module_error, e:
            pass
        except rights_error, e:
            if self.plugin_data["no_rights_error"] == 1:
                return ""

        self.page_msg( "Error run command:", e )
        return str(e)

    def _run_module_method(self, method_arguments={}):
        """
        Führt eine Methode eines Module aus.
        Kommt es irgendwo zu einem Fehler, ist es die selbsterstellte
        "run_module_error"-Exception mit einer passenden Fehlermeldung.
        """
        #~ if debug: self.page_msg("method_arguments:", method_arguments)

        #~ try:
        self.plugin_data.setup_module(self.module_name, self.main_method)
        #~ except KeyError:
            #~ raise run_module_error(
                #~ "[module name '%s' unknown (method: %s)]" % (self.module_name, self.main_method)
            #~ )

        #~ self.page_msg(self.module_name, self.main_method, self.plugin_data.keys())

        self.plugin_data.setup_URLs()
        self.plugin_data.check_rights()

        module_class = self._get_module_class()

        return self._run_method(module_class, method_arguments)


    def _get_module_class(self):
        """
        Importiert das Module und packt die Klasse als Objekt in self.data
        """
        def _import():
            return __import__(
                "%s.%s" % (self.plugin_data.package_name, self.module_name),
                {}, {}, [self.module_name]
            )

        if self.plugin_data.plugin_debug():
            self.page_msg(
                "Import module mit error handling: %s" % self.config.system.ModuleManager_error_handling
            )

        if self.config.system.ModuleManager_error_handling == False:
            import_object = _import()

        try:
            import_object = _import()
        except Exception, e:
            raise run_module_error(
                "[Can't import Modul '%s': %s]" % ( self.module_name, e )
            )

        try:
            return getattr(import_object, self.module_name)
        except Exception, e:
            raise run_module_error(
                "[Can't get class '%s' from module '%s': %s]" % ( self.module_name, self.module_name, e )
            )


    def _run_with_error_handling(self, unbound_method, method_arguments):
        if self.plugin_data.plugin_debug == True:
            self.page_msg("method_arguments for method '%s': %s" % (self.current_method, method_arguments))
        try:
            # Dict-Argumente übergeben
            return unbound_method(**method_arguments)
        except TypeError, e:
            sys.stdout = sys.__stdout__ # Evtl. redirectered stdout wiederherstellen

            if not str(e).startswith(unbound_method.__name__):
                # Der Fehler ist nicht hier, bei der Dict übergabe zur unbound_method() aufgetretten, sondern
                # irgendwo im Modul selber!
                raise run_module_error("Fehler im Modul: %s" % e)

            # Ermitteln der Argumente die wirklich von der unbound_method() verlangt werden
            import inspect
            args = inspect.getargspec(unbound_method)
            real_method_arguments = args[0][1:]
            real_method_arguments.sort()
            argcount = len(real_method_arguments)

            # Bessere Fehlermeldung generieren, wenn die von der Methode per get_CGI_data definierten Argumente
            # nicht in den CGI-Daten vorhanden sind.
            try:
                plugin_data_keys = self.plugin_data["get_CGI_data"].keys()
                plugin_data_keys.sort()
            except:
                plugin_data_keys=[]

            try:
                method_arguments_keys = method_arguments.keys()
                method_arguments_keys.sort()
            except:
                method_arguments_keys=[]

            raise run_module_error(
                "ModuleManager >get_CGI_data<-error: \
                %s() takes exactly %s arguments %s, \
                but %s existing in get_CGI_data config: %s, \
                and %s given from CGI data: %s \
                --- Compare the html form (internal page?), the get_CGI_data config and the real arguments in the method!" % (
                    unbound_method.__name__, argcount, real_method_arguments,
                    len(plugin_data_keys), plugin_data_keys,
                    len(method_arguments_keys), method_arguments_keys,
                )
            )


    def _run_method(self, module_class, method_arguments={}):
        """
        Startet die Methode und verarbeitet die Ausgaben
        """
        if method_arguments=={}:
            method_arguments = self.plugin_data.get_CGI_data
        #~ if debug: self.page_msg("method_arguments:", method_arguments)
        def run_error(msg):
            if self.plugin_data["direct_out"] != True:
                redirector.get() # stdout wiederherstellen

            msg = "[Can't run '%s.%s': %s]" % (self.module_name, self.current_method, msg)

            if self.config.system.ModuleManager_error_handling == True:
                raise run_module_error(msg)
            else:
                raise Exception(msg)


        # Instanz erstellen und PyLucid-Objekte übergeben
        if self.config.system.ModuleManager_error_handling == True:
            try:
                class_instance = module_class(self.PyLucid)
            except Exception, e:
                raise run_module_error(
                    "[Can't make class intance from module '%s': %s]" % (self.module_name, e)
                )
        else:
            class_instance = module_class(self.PyLucid)


        # Methode aus Klasse erhalten
        if self.config.system.ModuleManager_error_handling == True:
            try:
                unbound_method = getattr( class_instance, self.plugin_data.current_method )
            except Exception, e:
                raise run_module_error(
                    "[Can't get method '%s' from module '%s': %s]" % (
                        self.plugin_data.current_method, self.module_name, e
                    )
                )
        else:
            unbound_method = getattr( class_instance, self.plugin_data.current_method )

        if self.plugin_data["direct_out"] != True:
            # Alle print Ausgaben werden abgefangen und zwischengespeichert um diese in
            # die CMS Seite einbaunen zu können
            redirector = self.tools.redirector()

        # Methode "ausführen"
        if self.config.system.ModuleManager_error_handling == False:
            #~ self.page_msg(self.plugin_data.get_CGI_data)
            #~ direct_output = unbound_method(**self.plugin_data.get_CGI_data)
            #~ try:
            direct_output = self._run_with_error_handling(unbound_method, method_arguments)
            #~ except:
                #~ raise
        else:
            try:
                direct_output = self._run_with_error_handling(unbound_method, method_arguments)
            except SystemExit, e:
                if self.plugin_data["sys_exit"] == True:
                    # Modul macht evtl. einen sys.exit() (z.B. beim direkten Download, MySQLdump)
                    sys.exit()
                if direct_out != True: redirect_out = redirector.get() # stdout wiederherstellen
                # Beim z.B. page_style_link.print_current_style() wird ein sys.exit() ausgeführt
                self.page_msg(
                    "Error in Modul %s.%s: A Module can't use sys.exit()!" % (
                        self.module_name, self.current_method
                    )
                )
                direct_output = ""
            except KeyError, e:
                run_error("KeyError: %s" % e)
            except Exception, e:
                run_error(e)

        ##________________________________________________________________________________________
        ## Ausgaben verarbeiten

        if self.plugin_data["direct_out"] == True:
            # Das Modul kann direkte Ausgaben zum Browser machen (setzten von Cookies ect.)
            # Es kann aber auch Ausgaben zurückschicken die Angezeigt werden sollen (Login-Form)
            redirect_out = "" # Es gab keinen redirector
        else:
            # Zwischengespeicherte print Ausgaben zurückliefern
            redirect_out = redirector.get()

        if type(direct_output) == dict:
            try:
                content = direct_output["content"]
                markup  = direct_output["markup"]
            except KeyError, e:
                if self.plugin_data.plugin_debug:
                    self.page_msg( "Module-return is type dict, but there is no Key '%s'?!?" % e )
                result = str( direct_output )
            else:
                if self.plugin_data.plugin_debug == 1:
                    self.page_msg( "Apply markup '%s'." % markup )

                # Evtl. vorhandene stdout Ausgaben mit verarbeiten
                content = redirect_out + content

                # Markup anwenden
                direct_output = self.render.apply_markup( content, markup )
        elif direct_output == None:
            # Das Modul hat keine return-Daten, also wird es print Ausgaben gemacht haben,
            # diese werden weiterverarbeitet
            direct_output = redirect_out

        if self.plugin_data["has_Tags"] == True:
            # Die Ausgaben des Modules haben Tags, die aufgelöst werden sollen.
            if self.plugin_data.plugin_debug == True: self.page_msg( "Parse Tags." )
            return self.parser.parse( direct_output )

        return direct_output

    #________________________________________________________________________________________
    # Zusatz Methoden für die Module selber

    def build_menu(self):
        if debug:
            print "module_manager.build_menu():"
            print self.plugin_data.package_name
            print self.module_name
            print "self.plugin_data:", self.plugin_data.debug_data()

        menu_data = self.plugin_data.get_menu_data()
        print '<ul class="module_manager_menu">'
        for menu_section, section_data in menu_data.iteritems():
            print "<li><h5>%s</h5><ul>" % menu_section
            for item in section_data:
                print '<li><a href="%s&command=%s&action=%s">%s</a></li>' % (
                    self.URLs["base"], self.module_name, item["method_name"], item["menu_description"]
                )
            print "</ul>"
        print "</ul>"

class run_module_error(Exception):
    pass

class rights_error(Exception):
    """
    Ausführungsrechte Stimmen nicht
    """
    pass
















