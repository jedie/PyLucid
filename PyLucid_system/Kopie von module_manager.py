#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

# by jensdiemer.de (steht unter GPL-License)


"""

__version__="0.2.5"

__history__="""
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


import cgitb;cgitb.enable()
import sys, os, glob, imp, cgi, urllib

#~ print "Content-type: text/html; charset=utf-8\r\n" # Hardcore-Debugging ;)

#~ debug = False
debug = True

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

        self.CGI_dependency_checker = CGI_dependency_check( PyLucid )

        # Daten der Installierten Module holen
        self.data = self.db.get_active_module_data()
        if debug:
            self.page_msg("Available Modules:",self.data.keys())

    def run_tag( self, tag ):
        """
        Ausführen von:
        <lucidTag:'tag'/>
        """
        if tag.find(".") != -1:
            module_name, method_name = tag.split(".",1)
        else:
            module_name = tag
            method_name = "lucidTag"

        try:
            return self._run_module_method( module_name, method_name )
        except run_module_error, e:
            self.page_msg( "run tag %s, error '%s'" % (tag,e) )
            return str(e)

    def run_function( self, function_name, function_info ):
        """
        Ausführen von:
        <lucidFunction:'function_name'>'function_info'</lucidFunction>
        """
        module_name = function_name
        method_name = "lucidFunction"

        try:
            return self._run_module_method( module_name, method_name, function_info )
        except run_module_error, e:
            self.page_msg( "Error", e )
            return str(e)

    def run_command( self ):
        """
        ein Kommando ausführen.
        """
        try:
            command = self.CGIdata["command"]
            action = self.CGIdata["action"]
        except KeyError, e:
            self.page_msg( "Error in command: KeyError", e )
            return

        if debug == True: self.page_msg( "Command: %s; action: %s" % (command, action) )

        try:
            return self._run_module_method( command, action )
        except run_module_error, e:
            self.page_msg( "Error run command:", e )


    def _run_module_method(self, module_name, main_method, function_info=None):
        """
        Führt eine Methode eines Module aus.
        Kommt es irgendwo zu einem Fehler, ist es die selbsterstellte
        "run_module_error"-Exception mit einer passenden Fehlermeldung.
        """
        try:
            package_name = self.data[module_name]["package_name"]
        except KeyError:
            raise run_module_error(
                "[module name '%s' unknown (method: %s)]" % ( module_name, main_method )
            )

        module_id = self.data[module_name]["id"]

        module              = self._get_module( package_name, module_name )
        module_class        = self._get_module_class( module, module_name )
        method_properties   = self._get_method_properties( module_name, module_id, module_class, main_method )

        current_method = self.CGI_dependency_checker.get_current_method(
            module_name, method_properties, main_method, self.class_debug
        )
        if current_method != main_method:
            # Nach den CGI_dependency soll eine andere Methode soll ausgeführt werden
            # Die aktuelle Methode kann aber andere Einstellung für "direct_out", "apply_markup" usw. haben
            # deswegen aktualisieren wir die method_properties
            method_properties = self._get_CGI_dependency_properties( method_properties, current_method )

        if self.class_debug == True:
            self.page_msg( "current method_properties:", cgi.escape(str(method_properties)))

        try:
            self._check_rights( module_name, method_properties, module_class, main_method )
        except run_module_error, e:
            if method_properties.has_key( "no_rights_error" ) and \
            (method_properties["no_rights_error"] == True):
                return ""
            else:
                raise run_module_error( e )

        method_arguments = self._get_method_arguments( module_name, method_properties, function_info )

        class_instance  = self._make_class_instance( module_name, module_class )

        # Vorgefertigte Links in's Modul "einschleusen"
        self.put_data_to_module( module_name, class_instance, main_method, current_method )

        if method_properties.has_key("direct_out"):
            direct_out = method_properties["direct_out"]
        else:
            direct_out = False

        return self._run_method(
            module_name, class_instance, current_method, direct_out, method_arguments, method_properties
        )



    def _get_module( self, package_name, module_name ):
        """
        Liefert das Modul als Objekt zurück
        """
        def _import(package_name, module_name):
            return __import__(
                "%s.%s" % (package_name, module_name),
                globals(), locals(),
                [module_name]
            )

        if self.config.system.ModuleManager_error_handling == False:
            return _import(package_name, module_name)

        try:
            return _import(package_name, module_name)
        except Exception, e:
            raise run_module_error(
                "[Can't import Modul '%s': %s]" % ( module_name, e )
            )

    def _get_module_class( self, module, module_name ):
        """
        Liefert die Klasse im Module als Objekt zurück
        """
        try:
            return getattr( module, module_name )
        except Exception, e:
            raise run_module_error(
                "[Can't get class '%s' from module '%s': %s]" % ( module_name, module_name, e )
            )

    def _make_class_instance( self, module_name, module_class ):
        """
        Erstellt von der ungebundenen Klasse eine Instanz
        """
        if self.config.system.ModuleManager_error_handling == False:
            return module_class( self.PyLucid )
        try:
            return module_class( self.PyLucid )
        except TypeError,e:
            if str(e) == "this constructor takes no arguments":
                raise run_module_error(
                    "Error in Moduleclass %s, __init__(self, PyLucid) not exists. Org.Error: %s" % (
                        module_name, e
                    )
                )
            elif str(e).startswith("__init__"):
                raise run_module_error(
                    "Error in Moduleclass %s: __init__ must look like: __init__(self, PyLucid). Org.Error: %s" % (
                        module_name, e
                    )
                )
        except Exception, e:
                raise run_module_error(
                    "[Can't make instance from class %s: %s]" % (module_name, e)
                )

    def _get_method_properties( self, module_name, module_id, module_class, method ):
        """
        Liefert aus der Modul-Klasse die Module-Manager Einstellungen zurück
        """
        def check_type( module_name, data, info, method="" ):
            if type(data) != dict:
                raise run_module_error(
                    "[Wrong %s data for module %s %s]" % (info, module_name, method)
                )

        #~ method_data, CGI_dependent_data = self.db.get_method_properties(module_id, method)
        #~ self.page_msg("method_data:", method_data)
        #~ self.page_msg("CGI_dependent_data:", CGI_dependent_data)

        try:
            class_properties = getattr( module_class, "module_manager_data" )
        except Exception, e:
            raise run_module_error(
                "Can't get module_manager_data from %s for method %s" % (module_name, method)
            )
        if debug:
            self.page_msg("class_properties:", class_properties)

        check_type( module_name, class_properties, "module_manager_data" )

        if class_properties.has_key("debug"):
            self.class_debug = class_properties["debug"]
            if self.class_debug == True:
                self.page_msg( "-"*30 )
                self.page_msg("Debug for %s.%s:" % (module_class, method))
                self.CGIdata.debug()
        else:
            self.class_debug = False

        if self.class_debug == True:
            self.page_msg( "get_method_properties for method '%s'" % method )

        try:
            method_properties = class_properties[method]
        except Exception, e:
            if self.class_debug == True:
                self.page_msg( "Can't get rights for method: %s" % e )
                self.page_msg( "class_properties.keys():", class_properties.keys() )
            raise run_module_error(
                "%s has no rights defined for method '%s' or CGI_dependent_actions faulty (action value wrong?)" % (module_name, method)
            )

        check_type( module_name, method_properties, "module_manager_data", method )

        return method_properties


    def _get_CGI_dependency_properties( self, method_properties, current_method ):
        """
        Modifiziert die method_properties, mit Werten aus den CGI_dependent_actions der
        Aktuellen Methode.
        """
        def transfer_values( dict1, dict2, key_filter ):
            """
            Überträgt alle key/values von dict1 nach dict2, außer
            die keys aus der key_filter-Liste
            """
            for k,v in dict1.iteritems():
                if k in key_filter:
                    continue
                dict2[k] = v
            return dict2

        current_properties = method_properties["CGI_dependent_actions"][current_method]
        method_properties = transfer_values( current_properties, method_properties, ("CGI_laws", "CGI_must_have") )

        return method_properties


    def _check_rights( self, module_name, method_properties, module_class, method ):
        """
        Überprüft ob der aktuelle User das Modul überhaupt ausführen darf.
        """
        try:
            must_login = method_properties["must_login"]
        except Exception, e:
            must_login = True
            self.page_msg(
                "must_login not defined (%s) in Module %s for method %s" % (e, module_name, method)
            )

        if must_login == True:
            if self.session["user"] == False:
                raise run_module_error(
                    "[You must login to use %s for method %s]" % (module_name, method)
                )

            try:
                must_admin = method_properties["must_admin"]
            except Exception, e:
                must_admin = True
                self.page_msg(
                    "must_admin not defined (%s) in %s for method %s" % (e, module_name, method)
                )

            if (must_admin == True) and (self.session["isadmin"] == False):
                raise run_module_error(
                    "You must be an admin to use method %s from module %s!" % (method, module_name)
                )

    def _get_method_arguments(self, module_name, method_properties, function_info):
        """
        Wertet die 'get_CGI_data' Angaben aus.
            - Checkt die CGI-Daten
            - liefert Agumenten-Liste zurück
        """
        if function_info != None:
            # Informationen aus dem <lucidFunction>-Tag
            method_arguments = { "function_info": function_info }
            if self.class_debug == True:
                self.page_msg("function_info:", function_info)
        else:
            method_arguments = {}

        if not method_properties.has_key("get_CGI_data"):
            # Es gibt keine 'get_CGI_data'
            return method_arguments

        config = method_properties["get_CGI_data"]
        if self.class_debug == True:
            self.page_msg("'get_CGI_data'-config:", cgi.escape(str(config)))

        # Zahlen in den CGI-Daten werden in sessiondata.convert_types() automatisch
        # von string nach integer gewandelt!!!
        for arg_name, arg_type in config.iteritems():
            try:
                data = self.CGIdata[arg_name]
            except KeyError:
                if self.class_debug == True:
                    self.page_msg("Info: In CGI data Key '%s' not found. (Method use argument defaults?)" % arg_name)
                # Parameter auslassen
                continue

            if arg_type == str and type(data) != str:
                self.page_msg("TypeError: CGI-Data '%s' is not String!" % arg_name)
            elif arg_type == int and type(data) != int:
                self.page_msg("TypeError: CGI-Data '%s' is not a Integer!" % arg_name)

            method_arguments[arg_name] = data

        return method_arguments

    def put_data_to_module( self, module_name, class_instance, main_method, current_method ):
        """
        Daten (Link-URLs) in die Modul-Klasse "einfügen".
        """
        class_instance.link_url = "%s%s" % (
            self.config.system.poormans_url, self.config.system.page_ident
        )
        class_instance.base_url = "%s?page_id=%s" % (
            self.config.system.real_self_url, self.CGIdata["page_id"]
        )
        class_instance.command_url = "%s?page_id=%s&command=%s" % (
            self.config.system.real_self_url, self.CGIdata["page_id"], module_name
        )
        class_instance.action_url = "%s?page_id=%s&command=%s&action=" % (
            self.config.system.real_self_url, self.CGIdata["page_id"], module_name
        )
        class_instance.main_action_url = "%s?page_id=%s&command=%s&action=%s" % (
            self.config.system.real_self_url, self.CGIdata["page_id"], module_name, main_method
        )
        class_instance.current_action_url = "%s?page_id=%s&command=%s&action=%s" % (
            self.config.system.real_self_url, self.CGIdata["page_id"], module_name, current_method
        )
        # Zum automatischen erstellen eines Menüs:
        class_instance.module_manager_build_menu = self.build_menu



    def _run_method( self, module_name, class_instance, method, direct_out, method_arguments, method_properties ):
        """
        Startet die Methode und verarbeitet die Ausgaben
        """
        def run(method_arguments):
            if self.class_debug == True:
                self.page_msg("method_arguments for method '%s': %s" % (method, method_arguments))
            try:
                # Dict-Argumente übergeben
                return unbound_method(**method_arguments)
            except TypeError, e:
                if not str(e).startswith(unbound_method.__name__):
                    # Der Fehler ist nicht hier, bei der Dict übergabe zur unbound_method() aufgetretten, sondern
                    # irgendwo im Modul selber!
                    raise run_module_error("Fehler im Modul: %s" % e)

                # Ermitteln der Argumente die wirklich von der unbound_method() verlangt werden
                import inspect
                args = inspect.getargspec(unbound_method)
                real_method_arguments = args[0][1:]
                argcount = len(real_method_arguments)

                if not method_properties.has_key("get_CGI_data"):
                    # Fehler bei lucidFunction-Parameter übergabe
                    raise run_module_error(
                        "ModuleManager error: \
                        %s() takes exactly %s arguments %s, \
                        but %s given: %s \
                        --- Check the real arguments in the method!" % (
                            unbound_method.__name__, argcount, real_method_arguments,
                            len(method_arguments), str(method_arguments.keys()),
                        )
                    )

                # Bessere Fehlermeldung generieren, wenn die von der Methode per get_CGI_data definierten Argumente
                # nicht in den CGI-Daten vorhanden sind.
                raise run_module_error(
                    "ModuleManager >get_CGI_data<-error: \
                    %s() takes exactly %s arguments %s, \
                    but %s existing in get_CGI_data config: %s, \
                    and %s given from CGI data: %s \
                    --- Compare the html form (internal page?), the get_CGI_data config and the real arguments in the method!" % (
                        unbound_method.__name__, argcount, real_method_arguments,
                        len(method_properties["get_CGI_data"]), str(method_properties["get_CGI_data"].keys()),
                        len(method_arguments), str(method_arguments.keys()),
                    )
                )

        def run_error(module_name, method, msg):
            if direct_out != True:
                redirector.get() # stdout wiederherstellen

            msg = "[Can't run '%s.%s': %s]" % (module_name, method, msg)

            if self.config.system.ModuleManager_error_handling == True:
                raise run_module_error(msg)
            else:
                raise Exception(msg)

        # Methode aus Klasse erhalten
        if self.config.system.ModuleManager_error_handling == True:
            try:
                unbound_method = getattr( class_instance, method )
            except Exception, e:
                raise run_module_error(
                    "[Can't get method '%s' from module '%s': %s]" % ( method, module_name, e )
                )
        else:
            unbound_method = getattr( class_instance, method )


        if direct_out != True:
            # Alle print Ausgaben werden abgefangen und zwischengespeichert um diese in
            # die CMS Seite einbaunen zu können
            redirector = self.tools.redirector()



        # Methode "ausführen"
        if self.config.system.ModuleManager_error_handling == False:
            direct_output = unbound_method(**method_arguments)
        else:
            try:
                direct_output = run(method_arguments)
            except SystemExit, e:
                if method_properties.has_key("sys_exit") and method_properties["sys_exit"] == True:
                    # Modul macht evtl. einen sys.exit() (z.B. beim direkten Download, MySQLdump)
                    sys.exit()
                if direct_out != True: redirect_out = redirector.get() # stdout wiederherstellen
                # Beim z.B. page_style_link.print_current_style() wird ein sys.exit() ausgeführt
                self.page_msg("Error in Modul %s.%s: A Module can't use sys.exit()!" % (module_name, method))
                direct_output = ""
            except KeyError, e:
                run_error(module_name, method, "KeyError: %s" % e)
            except Exception, e:
                run_error(module_name, method, e)

        ##________________________________________________________________________________________
        ## Ausgaben verarbeiten

        if direct_out == True:
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
                if self.class_debug:
                    self.page_msg( "Module-return is type dict, but there is no Key '%s'?!?" % e )
                result = str( direct_output )
            else:
                if self.class_debug == True: self.page_msg( "Apply markup '%s'." % markup )

                # Evtl. vorhandene stdout Ausgaben mit verarbeiten
                content = redirect_out + content

                # Markup anwenden
                direct_output = self.render.apply_markup( content, markup )
        elif direct_output == None:
            # Das Modul hat keine return-Daten, also wird es print Ausgaben gemacht haben,
            # diese werden weiterverarbeitet
            direct_output = redirect_out

        if method_properties.has_key("has_Tags") and method_properties["has_Tags"] == True:
            # Die Ausgaben des Modules haben Tags, die aufgelöst werden sollen.
            if self.class_debug == True: self.page_msg( "Parse Tags." )
            return self.parser.parse( direct_output )

        return direct_output

    #________________________________________________________________________________________

    def build_menu( self, module_manager_data, action_url ):
        """
        Generiert automatisch aus den module_manager_data ein "Action"-Menü.
        Wird zur aufgerufenden Klasse übertragen.
        """
        menu_data = {}
        for method, data in module_manager_data.iteritems():
            #~ self.page_msg( method, data )
            try:
                data = data["menu_info"]
            except:
                #~ self.page_msg( "No menu_info for %s" % method )
                continue

            try:
                section     = data["section"]
                description = data["description"]
            except Exception, e:
                self.page_msg( "Error in menu_info:", e )
                continue

            if not menu_data.has_key( section ):
                menu_data[section] = []

            menu_data[section].append(
                [ method, description ]
            )

        #~ self.page_msg( "Debug:", menu_data )

        print "<ul>"
        for section, data in menu_data.iteritems():
            print "\t<li><h5>%s</h5>" % section
            print "\t<ul>"
            for item in data:
                print '\t\t<li><a href="%s%s">%s</a></li>' % (
                    action_url, item[0], item[1]
                )
            print "\t</ul>"
            print "\t</li>"
        print "</ul>"

    #________________________________________________________________________________________

    def debug( self ):
        import inspect
        self.page_msg( "-"*30 )
        self.page_msg(
            "ModuleManager Debug (from '...%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )
        for module_name, package_name  in self.data.iteritems():
            self.page_msg( "%s.%s" % (package_name, module_name) )
        self.page_msg( "-"*30 )


class run_module_error(Exception):
        pass



class CGI_dependency_check:
    def __init__( self, PyLucid ):
        self.CGIdata    = PyLucid["CGIdata"]
        self.page_msg   = PyLucid["page_msg"]

    def get_current_method( self, module_name, method_properties, main_method, debug ):
        """
        Wertet CGI_dependent_actions in den method_properties aus.
        """
        self.module_name    = module_name
        self.main_method    = main_method
        self.debug          = debug

        if not method_properties.has_key("CGI_dependent_actions"):
            # Es gibt keine CGI-Daten abhängige Funktionen
            if self.debug == True:
                self.page_msg(
                    "Info: No CGI_dependent_actions found in %s %s" % (module_name, main_method)
                )
            return main_method

        CGI_dependent_actions = method_properties["CGI_dependent_actions"]
        if type( CGI_dependent_actions ) != dict:
            raise run_module_error(
                "[Error in CGI_dependent_actions Format for %s.%s]" % ( module_name, main_method )
            )

        for method,dependency in CGI_dependent_actions.iteritems():
            if self.check_dependency( dependency, method ) == True:
                # Eine Abhängige methode ist vorhanden
                if self.debug == True:
                    self.page_msg( "current method: %s" % method )
                return method

        if self.debug == True:
            self.page_msg( "current method: %s" % main_method )
        return main_method

    def check_dependency( self, dependency, sub_method ):
        """
        CGI_dependent_actions
        """
        if self.debug == True: self.page_msg( "*** check sub_method %s:" % sub_method )

        if type( dependency ) != dict:
            self.page_msg(
                "Error in CGI_dependent_actions. Modul %s method %s: \
                statements is not from type dict." % (
                    self.module_name, sub_method
                )
            )
            return False

        if not (dependency.has_key("CGI_laws") or dependency.has_key("CGI_must_have") ):
            self.page_msg(
                "Error in CGI_dependent_actions. Modul %s method %s: \
                statements has no key CGI_laws or CGI_must_have" % (
                    self.module_name, sub_method
                )
            )
            return False

        if dependency.has_key( "CGI_laws" ):
            if self._check_CGI_laws( dependency["CGI_laws"] ) != True:
                if self.debug == True: self.page_msg( "check_CGI_laws failt" )
                return False
            else:
                if self.debug == True: self.page_msg( "CGI_laws OK" )
        else:
            if self.debug == True: self.page_msg( "no CGI_laws defined" )

        if dependency.has_key( "CGI_must_have" ):
            if not type( dependency["CGI_must_have"] ) in (list,tuple):
                self.page_msg(
                    "Error in CGI_dependent_actions. Modul %s method %s: \
                    CGI_must_have statements are not type list or tuple." % (
                            self.module_name, sub_method
                        )
                    )
                return False
            if self._check_CGI_has_keys( dependency["CGI_must_have"] ) != True:
                if self.debug == True: self.page_msg( "CGI_must_have failt" )
                return False
            else:
                if self.debug == True: self.page_msg( "CGI_must_have OK" )
        else:
            if self.debug == True: self.page_msg( "no CGI_must_have defined" )

        if self.debug == True: self.page_msg( "CGI_dependent_actions OK" )
        return True

    def _check_CGI_has_keys( self, keys ):
        for key in keys:
            if not self.CGIdata.has_key( key ):
                if self.debug == True:
                    self.page_msg( "Error: key '%s' not found in keys %s" % (key,keys) )
                return False
        return True

    def _check_CGI_laws( self, CGI_laws ):
        for key,value in CGI_laws.iteritems():

            if not self.CGIdata.has_key( key ):
                if self.debug == True:
                    self.page_msg( "key %s not found in CGI_laws (%s)" % (key,CGI_laws) )
                return False

            if type( value ) == str: # Soll festgelegten String entsprechen
                if not self.CGIdata[key] == value:
                    if self.debug == True:
                        self.page_msg(
                            "Error in CGIdata for %s: CGIdata key %s is not equal %s" % (
                                self.module_name, key, value
                            )
                        )
                    return False
                return True
            elif type( value ) == int: # Soll einer bestimmten Zahl entsprechen
                try:
                    self.CGIdata[key] = int( self.CGIdata[key] )
                except Exception, e:
                    self.page_msg(
                        "Error in CGIdata for %s: Can't konvert CGIdata key %s to type int" % (
                            self.module_name, key
                        )
                    )
                    return False
                if not self.CGIdata[key] == value:
                    if self.debug == True:
                        self.page_msg(
                            "Error in CGIdata for %s: CGIdata key %s is not equal to %s" % (
                                self.module_name, key, value
                            )
                        )
                    return False
                return True
            elif value == int: # value muß einfach nur irgendeine Zahl sein
                try:
                    self.CGIdata[key] = int( self.CGIdata[key] )
                except Exception, e:
                    self.page_msg(
                        "Error in CGIdata for %s: CGIdata key %s is not type int" % (
                            self.module_name, key
                        )
                    )
                    return False
                return True
            else:
                self.page_msg(
                    "Error in CGI_dependent_actions for %s: \
                    The CGI_law type %s for key %s not supported (Use CGI_must_have ?!?)" % (
                        self.module_name, cgi.escape( str(value) ), key
                    )
                )
                return False






