#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Admin

Einrichten/Konfigurieren von Modulen und Plugins

CREATE TABLE `lucid_plugindata` (
  `id` int(11) NOT NULL auto_increment,
  `plugin_id` int(11) NOT NULL default '0',
  `method_name` varchar(50) NOT NULL default '',
  `parent_method_id` int(11) default NULL,
  `CGI_laws` varchar(255) default NULL,
  `get_CGI_data` varchar(255) default NULL,
  `internal_page_info` varchar(255) default NULL,
  `menu_section` varchar(128) default NULL,
  `menu_description` varchar(255) default NULL,
  `must_admin` int(11) NOT NULL default '1',
  `must_login` int(11) NOT NULL default '1',
  `has_Tags` int(11) NOT NULL default '0',
  `no_rights_error` int(11) NOT NULL default '0',
  `direct_out` int(11) NOT NULL default '0',
  `sys_exit` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `combinedKey` (`plugin_id`,`method_name`)
);

CREATE TABLE `lucid_plugins` (
  `id` int(11) NOT NULL auto_increment,
  `package_name` varchar(30) NOT NULL default '',
  `module_name` varchar(30) NOT NULL default '',
  `version` varchar(15) default NULL,
  `author` varchar(50) default NULL,
  `url` varchar(128) default NULL,
  `description` varchar(255) default NULL,
  `long_description` text,
  `active` int(1) NOT NULL default '0',
  `debug` int(1) NOT NULL default '0',
  `SQL_deinstall_commands` text,
  PRIMARY KEY  (`id`)
);
"""

__version__="0.1.1"

__history__="""
v0.1.1
    - NEU: reinit
v0.1
    - erste Version
"""

__todo__="""
    - CSS deinstallation
    - Fehlerausgabe bei check_module_data
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\nDEBUG!" # Debugging

import sys, os, glob, imp, cgi, urllib, pickle


debug = False
#~ debug = True
error_handling = False
available_packages = ("PyLucid_modules","PyLucid_buildin_plugins","PyLucid_plugins")
internal_page_file = "PyLucid_modules/module_admin_administation_menu.html"




class module_admin:

    def __init__(self, PyLucid, call_from_install_PyLucid=False):
        self.page_msg       = PyLucid["page_msg"]
        self.db             = PyLucid["db"]
        if debug == True: self.db.debug = True
        self.URLs           = PyLucid["URLs"]
        self.module_manager = PyLucid["module_manager"]
        self.call_from_install_PyLucid = call_from_install_PyLucid

    def menu(self):
        print "<h4>Module/Plugin Administration v%s</h4>" % __version__
        self.module_manager.build_menu()#self.module_manager_data, self.URLs["action"] )

    def link(self, action):
        print '<p><a href="%s%s">%s</a></p>' % (self.URLs["action"], action, action)

    def administation_menu(self, print_link=True):
        """
        Module/Plugins installieren
        """
        self.installed_modules_info = self.get_installed_modules_info()
        if debug:
            self.page_msg(self.installed_modules_info)

        data = self._read_packages()
        data = self._filter_cfg(data)
        data = self._read_all_moduledata(data)

        context_dict = {
            "version"       : __version__,
            "package_data"  : data,
            "installed_data": self.installed_modules_info,
            "action_url"    : self.URLs["action"],
        }

        if self.call_from_install_PyLucid == True:
            # Wurde von install_PyLucid.py aufgerufen.
            from PyLucid_simpleTAL import simpleTAL, simpleTALES

            context = simpleTALES.Context(allowPythonPath=1)
            context.globals.update(context_dict) # context.addGlobal()

            try:
                f = file(internal_page_file,"rU")
                install_template = f.read()
                f.close()
            except Exception, e:
                print "Can't read internal_page file '%s': %s" % (internal_page_file, e)
                return

            template = simpleTAL.compileHTMLTemplate(install_template, inputEncoding="UTF-8")
            template.expand(context, sys.stdout, outputEncoding="UTF-8")
        else:
            # Normal als Modul aufgerufen
            self.db.print_internal_TAL_page("administation_menu", context_dict)
            self.link("menu")

    def debug_data(self):
        data = self._read_packages()
        data, installed_data = self._filter_cfg(data)
        data = self._read_all_moduledata(data)

        self.link("menu")
        self.debug_package_data(data)
        self.link("menu")

    #________________________________________________________________________________________

    def first_time_install(self):
        print "First Time Install!!!"
        print "<pre>"
        print "truncate table plugins and plugindata...",
        try:
            self.db.cursor.execute("TRUNCATE TABLE %splugins" % self.db.tableprefix)
            self.db.cursor.execute("TRUNCATE TABLE %splugindata" % self.db.tableprefix)
        except Exception, e:
            print "Error:", e
            print "You must first init the table!!!"
            return
        else:
            print "OK"

        self.installed_modules_info = [] # Wir tun mal so, als wenn es keine installierten Module gibt
        data = self._read_packages()
        data = self._filter_cfg(data)
        data = self._read_all_moduledata(data)

        sorted_data = []
        for module in data:
            if (module["essential_buildin"] != True) and (module["important_buildin"] != True):
                continue

            try:
                self.install(module['package_name'], module['module_name'], print_info=False)
            except Exception, e:
                print "*** Error:", e

            # essential_buildin werden automatisch aktiviert mit active = -1
            # important_buildin müßen normal aktiviert werden (active = 1)
            if module["important_buildin"] == True:
                print "Activate plugin with ID:",self.registered_plugin_id
                self.activate(self.registered_plugin_id, print_info=False)

        print "</pre>"


    #________________________________________________________________________________________

    def register_methods(self, package, module_name, module_data):
        """
        Das module_manager_data Dict aufbereitet in die DB schreiben
        """
        def register_method(plugin_id, method, method_data):
            for k,v in method_data.iteritems():
                print "***", k, "-", v

        print "Find id for %s.%s..." % (package, module_name),
        try:
            plugin_id = self.db.get_plugin_id(package, module_name)
        except Exception, e:
            if not error_handling: raise Exception(e)
            print "ERROR:", e
        else:
            print "OK, id is:", plugin_id
        print

        # module_manager_data in Tabelle "plugindata" eintragen
        print "register methods:"
        for method_name in module_data["module_manager_data"]:
            print "*", method_name,
            method_cfg = module_data["module_manager_data"][method_name]

            if type(method_cfg) != dict:
                print "- Error, %s-value, in module_manager_data, is not typed dict!!!" % method_name
                continue

            method_cfg = method_cfg.copy()

            if method_cfg.has_key('CGI_dependent_actions'):
                del method_cfg['CGI_dependent_actions']

            try:
                self.db.register_plugin_method(plugin_id, method_name, method_cfg)
            except Exception, e:
                print "Error:", e
            else:
                print "OK"
        print

        for parent_method in module_data["module_manager_data"]:
            method_cfg = module_data["module_manager_data"][parent_method]

            if type(method_cfg) != dict:
                print "Error in data!!!"
                continue

            if not method_cfg.has_key('CGI_dependent_actions'):
                continue

            dependent_cfg = method_cfg['CGI_dependent_actions']

            parent_cfg = method_cfg
            del parent_cfg['CGI_dependent_actions']

            try:
                parent_method_id = self.db.get_method_id(plugin_id, parent_method)
            except Exception, e:
                print "ERROR: Can't get parent method ID for plugin_id '%s' and method_name '%s'" % (
                    plugin_id, parent_method
                )
                continue

            print "register CGI_dependent_actions for method '%s' with id '%s':" % (
                parent_method, parent_method_id
            )

            for method_name, cfg in dependent_cfg.iteritems():
                print "*",method_name,

                try:
                    self.db.register_plugin_method(plugin_id, method_name, cfg, parent_method_id)
                except Exception, e:
                    print "Error:", e
                else:
                    print "OK"
            print

    #________________________________________________________________________________________
    # install

    def install(self, package, module_name, print_info=True):
        """
        Modul in die DB eintragen
        """
        if print_info:
            self.link("administation_menu")
            print "<h3>Install %s.%s</h3>" % (package, module_name)
            print "<pre>"
        else:
            print "_"*80
            print "Install %s.%s" % (package, module_name)

        module_data = self._get_module_data(package, module_name)

        if self.check_module_data(module_data) == True:
            print "<h3>Error</h3><h4>module config data failed. Module was not installed!!!</h4>"
            self.debug_package_data([module_data])
            return

        #~ self.debug_package_data([module_data])

        ##_____________________________________________
        # In Tabelle "plugins" eintragen
        print "register plugin %s.%s..." % (package, module_name),
        #~ print package, module_name
        #~ print module_data
        try:
            self.registered_plugin_id = self.db.install_plugin(module_data)
        except Exception, e:
            print "ERROR:", e
            # Wahscheinlich ist das Plugin schon installiert.
            try:
                self.registered_plugin_id = self.db.get_plugin_id(module_data['package_name'], module_data['module_name'])
            except Exception, e:
                print "Can't get Module/Plugin ID:", e
                print "Aborted!"
                return
        else:
            print "OK"
        print

        ##_____________________________________________
        # Stylesheets
        if module_data["styles"] != None:
            print "install stylesheet:"
            for style in module_data["styles"]:
                print "* %-25s" % style["name"],
                css_filename = os.path.join(
                    module_data['package_name'],
                    "%s_%s.css" % (module_data['module_name'], style["name"])
                )
                print "%s..." % css_filename,
                try:
                    f = file(css_filename, "rU")
                    style["content"] = f.read()
                    f.close()
                except Exception, e:
                    print "Error reading CSS-File: %s" % e
                    return
                else:
                    try:
                        style["plugin_id"] = self.registered_plugin_id
                        self.db.new_style(style)
                    except Exception, e:
                        print "Error:", e
                    else:
                        print "OK"
            print

        ##_____________________________________________
        # internal_pages
        print "install internal_page:"
        for method_name, method_data in module_data["module_manager_data"].iteritems():
            self._install_internal_page(method_data, package, module_name, method_name)

            if type(method_data) == dict and method_data.has_key("CGI_dependent_actions"):
                for method_name, CGI_dependent_method_data in method_data["CGI_dependent_actions"].iteritems():
                    self._install_internal_page(CGI_dependent_method_data, package, module_name, method_name)
        print

        ##_____________________________________________
        # SQL Kommandos ausführen
        if module_data["SQL_install_commands"] != None:
            self.execute_SQL_commands(module_data["SQL_install_commands"])
            print

        self.register_methods(package, module_name, module_data)

        if print_info:
            print "</pre>"
            print 'activate this Module? <a href="%sactivate&id=%s">yes, enable it</a>' % (
                self.URLs["action"], self.registered_plugin_id
            )
            self.link("administation_menu")

    def _install_internal_page(self, method_data, package, module_name, method_name):
        """
        Eintragen der internal_page
        Wird von self.install() benutzt
        """
        if type(method_data) != dict or method_data.has_key("internal_page_info") != True:
            return

        data = method_data["internal_page_info"]
        #~ print "X", data
        internal_page = {
            "name"          : data.get("name",method_name),
            "plugin_id"     : self.registered_plugin_id,
            "description"   : data["description"],
            "markup"        : data["markup"]
        }

        print "* %-25s" % internal_page["name"],

        internal_page_filename = os.path.join(
            package, "%s_%s.html" % (module_name, internal_page["name"])
        )
        print "%s..." % internal_page_filename,
        try:
            lastupdatetime = os.stat(internal_page_filename).st_mtime
        except:
            lastupdatetime = None

        try:
            f = file(internal_page_filename, "rU")
            internal_page["content"] = f.read()
            f.close()
        except Exception, e:
            print "Error reading Template-File: %s" % e
        else:
            try:
                self.db.new_internal_page(internal_page, lastupdatetime)
            except Exception, e:
                print "Error:", e
            else:
                print "OK"


    def check_module_data(self, data):

        def check_dict_list(dict_list, type, must_have_keys):
            errors = False
            for item in dict_list:
                for key in must_have_keys:
                    if not item.has_key(key):
                        self.page_msg("&nbsp;-&nbsp;KeyError in %s: %s" % (type, key))
                        errors = True
            return errors

        has_errors = False
        if data["styles"] != None:
            status = check_dict_list(
                data["styles"], "styles",
                ("name", "description")
            )
            if status == True: has_errors=True

        return has_errors

    #________________________________________________________________________________________
    # DEinstall

    def deinstall(self, id, print_info=True):
        """
        Modul aus der DB löschen
        """
        try:
            deinstall_info = self.db.get_module_deinstall_info(id)
        except IndexError:
            self.page_msg("Can't get plugin with id '%s'! Is this Plugin is installed?!?!" % id)
            self.administation_menu()
            return

        if print_info:
            print "<h3>DEinstall Plugin %s.%s (ID %s)</h3>" % (
                deinstall_info["package_name"], deinstall_info["module_name"], id)

            self.link("administation_menu")
            print "<pre>"

        ##_____________________________________________
        # Einträge in Tabelle 'plugindata' löschen
        print "delete plugin-data...",
        try:
            self.db.delete_plugindata(id)
        except Exception, e:
            print "Error:", e
        else:
            print "OK"

        ##_____________________________________________
        # Einträge in Tabelle 'plugin' löschen
        print "delete plugin registration...",
        try:
            self.db.delete_plugin(id)
        except Exception, e:
            print "Error:", e
        else:
            print "OK"

        print

        ##_____________________________________________
        # Stylesheets löschen
        print "delete stylesheet...",
        try:
            deleted_styles = self.db.delete_style_by_plugin_id(id)
        except Exception, e:
            print "ERROR:", e
        else:
            print "OK, deleted:", deleted_styles
        print

        ##_____________________________________________
        # internal_pages löschen
        print "delete internal_pages...",
        try:
            deleted_pages = self.db.delete_internal_page_by_plugin_id(id)
        except Exception, e:
            print "ERROR:", e
        else:
            print "OK, deleted pages: %s" % deleted_pages
        print

        ##_____________________________________________
        # SQL Kommandos ausführen
        if deinstall_info["SQL_deinstall_commands"] != None:
            self.execute_SQL_commands(deinstall_info["SQL_deinstall_commands"])

        if print_info:
            print "</pre>"
            self.link("administation_menu")

    #________________________________________________________________________________________
    # REinit (Ein Modul/Plugin deinstallieren und direkt wieder Installieren)

    def reinit(self, id):
        self.link("administation_menu")

        try:
            package_name, module_name = self.db.get_plugin_info_by_id(id)
        except Exception, e:
            print "ERROR: Can't get plugin information (ID %s): %s" % (id, e)
            return

        print "<h3>reinit Plugin %s.%s (ID %s)</h3>" % (package_name, module_name, id)

        print "<pre>"

        print " *** deinstall ***"
        self.deinstall(id, print_info=False)

        print " *** install ***"
        self.install(package_name, module_name, print_info=False)

        print "</pre>"
        self.link("administation_menu")

    #________________________________________________________________________________________
    # Activate / Deactivate

    def activate(self, id, print_info=True):
        self.db.activate_module(id)
        if print_info==True:
            self.page_msg("Enable Module/Plugin (ID: %s)" % id)
            self.administation_menu()

    def deactivate(self, id):
        self.db.deactivate_module(id)
        self.page_msg("Disable Module/Plugin (ID: %s)" % id)
        self.administation_menu()

    #________________________________________________________________________________________
    # Information über nicht installierte Module / Plugins

    def _read_one_package(self, package_name):
        """
        Dateiliste eines packages erstellen.
        """
        filelist = []
        for module_path in glob.glob( "%s/*.py" % package_name ):
            filename = os.path.split( module_path )[1]
            if filename[0] == "_": # Dateien wie z.B. __ini__.py auslassen
                continue
            module_name = os.path.splitext( filename )[0]
            filelist.append(module_name)
        return filelist

    def _read_packages(self):
        """
        Alle verfügbaren packages durch scannen.
        """
        data = {}
        for package in available_packages:
            filelist = self._read_one_package(package)
            for filename in filelist:
                if data.has_key(filename):
                    self.page_msg("Error: duplicate Module/Pluginname '%s'!" % filename)
                data[filename] = {"package": package}
        return data

    def is_installed(self, package, module):
        for line in self.installed_modules_info:
            if line["package_name"] == package and line["module_name"] == module:
                return True
        return False

    def _filter_cfg(self, package_data):
        """
        Nur Module/Plugins herrausfiltern zu denen es auch Konfiguration-Daten gibt.
        """
        not_installed_data = {}
        installed_data = []
        filelist = package_data.keys()
        for module_name, module_data in package_data.iteritems():
            if not module_name.endswith("_cfg"):
                continue

            clean_module_name = module_name[:-4]
            if not clean_module_name in filelist:
                # Zur Config-Datei gibt's kein Module?!? -> Wird ausgelassen
                continue

            if self.is_installed(module_data["package"], clean_module_name):
                # Schon installierte Module auslassen
                continue

            # Das Modul ist noch nicht installiert!
            not_installed_data[clean_module_name] = module_data
            not_installed_data[clean_module_name]["cfg_file"] = module_name

        return not_installed_data

    def _get_module_data(self, package, module_name):
        """
        Liefert alle Daten zu einem Modul.
        """
        def _import(package_name, module_name):
            #~ print package_name, module_name
            return __import__(
                "%s.%s" % (package_name, module_name),
                globals(), locals(),
                [module_name]
            )

        try:
            module_cfg_object = _import(package, module_name+"_cfg")
        except SyntaxError, e:
            raise SyntaxError("Can't import %s.%s: %s" % (package, module_name, e))

        result = {
            "package_name"  : package,
            "module_name"   : module_name,
        }

        try:
            result["module_manager_data"] = getattr(module_cfg_object, "module_manager_data")
        except AttributeError, e:
            self.page_msg("Can't get module_manager_data from %s: %s" % (module_name+"_cfg",e))
            # Die ModuleManager-Daten _müßen_ vorhanden sein, deswegen wird jetzt das
            # ganze Module ausgelassen
            return

        def get_striped_attr(object, attr):
            result = getattr(object, attr, None)
            if type(result) == str:
                return result.strip()
            return result

        result["module_manager_debug"] = getattr(module_cfg_object, "module_manager_debug", False)

        # Normale Attribute holen
        for attr in ("SQL_install_commands", "SQL_deinstall_commands", "styles", "internal_pages"):
            result[attr] = get_striped_attr(module_cfg_object, attr)

        # meta Attribute holen
        for attr in ("author", "url", "description", "long_description", "essential_buildin", "important_buildin"):
            result[attr] = get_striped_attr(module_cfg_object, "__%s__" % attr)

        # Versions-Information aus dem eigentlichen Module holen
        module_cfg_object = _import(package, module_name)
        result["version"] = get_striped_attr(module_cfg_object, "__version__")

        result = self._prepare_module_data(result)

        return result

    def _read_all_moduledata(self, package_data):
        """
        Einlesen der Einstellungsdaten aus allen Konfigurationsdateien
        """
        result = []
        for module_name, module_data in package_data.iteritems():
            #~ print module_name
            try:
                module_data.update(self._get_module_data(module_data["package"], module_name))
            except Exception, e:
                self.page_msg("Can't get Data for %s.%s: %s" % (module_data["package"], module_name, e))
                continue

            module_data["module_name"] = module_name
            result.append(module_data)
        return result

    def _prepare_module_data(self, module_data):
        """
        Aufbereiten der Daten für die installation:
            - Deinstallationsdaten serialisieren
        """
        # Deinstallationsdaten serialisieren
        if module_data["SQL_deinstall_commands"] != None:
            module_data["SQL_deinstall_commands"] = pickle.dumps(module_data["SQL_deinstall_commands"])

        return module_data

    #________________________________________________________________________________________
    # Informationen über in der DB installierte Module / Plugins

    def get_installed_modules_info(self):
        try:
            installed_modules_info = self.db.get_installed_modules_info()
        except Exception, e:
            print "Content-type: text/html; charset=utf-8\r\n\r\n"
            print "<h1>Can't get installed module data from DB:</h1>"
            print "<h4>%s</h4>" % e
            print "<h3>Did you run install_PyLucid.py ???</h3>"
            sys.exit()
        return installed_modules_info

    #________________________________________________________________________________________
    # Hilfs methoden

    def execute_SQL_commands(self, command_list):
        """
        Wird beim installalieren und deinstallieren verwendet.
        """
        for command in command_list:
            print "execute '%s...'" % cgi.escape(" ".join(command.split(" ",3)[:3])),
            try:
                self.db.get(command)
            except Exception, e:
                print "Error: %s" % e
            else:
                print "OK"

    def debug_package_data(self, data):
        print "<h3>Debug package data:</h3>"
        for module_data in data:
            keys = module_data.keys()
            keys.sort()
            print "<h3>%s</h3>" % module_data["module_name"]
            print "<pre>"
            for key in keys:
                value = module_data[key]
                if type(value) == dict: # module_manager_data
                    print " -"*40
                    print "%22s :" % key
                    keys2 = value.keys()
                    keys2.sort()
                    for key2 in keys2:
                        print "\t%20s : %s" % (key2,cgi.escape(str(value[key2]).encode("String_Escape")))
                    print " -"*40
                else:
                    print "%22s : %s" % (key,cgi.escape(str(value).encode("String_Escape")))
            print "</pre>"




