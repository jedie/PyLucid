#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Admin

Einrichten/Konfigurieren von Modulen und Plugins


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

__todo__="""
Diese aktuelle Version ist Mist! Aber es funktioniert ;(

    - Fehlerausgabe bei check_moduleData
"""


import sys, os, glob, imp, cgi, urllib, pickle


debug = False
#~ debug = True

error_handling = False
package_basedir = "PyLucid"
available_packages = ("modules","buildin_plugins","plugins")
# Wenn es von _install Aufgerufen wird, wird das Template von Platte gelesen:
internal_page_file = "PyLucid/modules/module_admin/administation_menu.html"
internal_page_css = "PyLucid/modules/module_admin/administation_menu.css"


from PyLucid.components import plugin_cfg

from PyLucid.system.exceptions import *
from PyLucid.system.BaseModule import PyLucidBaseModule








class module_admin(PyLucidBaseModule):
    #~ def __init__(self, *args, **kwargs):
        #~ super(ModuleAdmin, self).__init__(*args, **kwargs)

    def menu(self):
        if "install" in self.request.form:
            self.request.db.commit()
            package_name = self.request.form["package_name"]
            moduleName = self.request.form["module_name"]
            #~ try:
            self.install(package_name, moduleName)
            #~ except IntegrityError, e:
                #~ self.response.write("DB Error: %s\n" % e)
                #~ self.request.db.rollback()
                #~ self.response.write("(execute DB rollback)")
            #~ except KeyError, e:
                #~ self.response.write("KeyError: %s" % e)
            #~ else:
                #~ self.request.db.commit()
            #~ return
        elif "deinstall" in self.request.form:
            id = self.request.form["id"]
            #~ try:
            self.deinstall(id)
            #~ except IntegrityError, e:
                #~ self.response.write("DB Error: %s\n" % e)
                #~ self.request.db.rollback()
                #~ self.response.write("(execute DB rollback)")
            #~ else:
                #~ self.request.db.commit()
            #~ return
        elif "reinit" in self.request.form:
            id = self.request.form["id"]
            try:
                self.reinit(id)
            except IntegrityError, e:
                self.response.write("DB Error: %s\n" % e)
                self.request.db.rollback()
                self.response.write("(execute DB rollback)")
            #~ except KeyError, e:
                #~ self.response.write("KeyError: %s" % e)
            else:
                self.request.db.commit()
        elif "activate" in self.request.form:
            id = self.request.form["id"]
            try:
                self.activate(id)
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
        elif "deactivate" in self.request.form:
            id = self.request.form["id"]
            try:
                self.deactivate(id)
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
        #~ elif sub_action == "module_admin_info":
            #~ self.module_admin_info()
            #~ return
        #~ elif sub_action == "administation_menu":
            #~ self._write_backlink()
        #~ elif sub_action == "init_modules":
            #~ self.print_backlink()
            #~ if self.CGIdata.get("confirm","no") == "yes":
                #~ module_admin = self._get_module_admin()
                #~ self.first_time_install_confirmed()
            #~ self._write_backlink()
            #~ return

        self.administation_menu()

    def link(self, action):
        if self.request.runlevel != "install":
            # Nur wenn nicht im "install" Bereich
            self.response.write(
                '<p><a href="%s%s">%s</a></p>' % (
                    self.URLs["action"], action, action
                )
            )

    def administation_menu(self, print_link=True):
        """
        Module/Plugins installieren
        """
        moduleData = Modules(self.request, self.response)
        moduleData.readAllModules()
        if debug:
            moduleData.debug()

        moduleData = moduleData.getModuleStatusList()

        context_dict = {
            "version"       : __version__,
            "moduleData"    : moduleData,
            "action_url"    : self.URLs.currentAction(),
        }

        if self.runlevel.is_install():
            try:
                f = file(internal_page_file,"rU")
                install_template = f.read()
                f.close()
            except Exception, e:
                self.response.write(
                    "Can't read internal_page file '%s': %s" % (
                        internal_page_file, e
                    )
                )
                return

            from PyLucid.system.template_engines import render_jinja
            content = render_jinja(install_template, context_dict)
            self.response.write(content)

            # CSS Daten einfach rein schreiben:
            try:
                f = file(internal_page_css, "rU")
                cssData = f.read()
                f.close()
            except:
                pass
            else:
                self.response.write('<style type="text/css">')
                self.response.write(cssData)
                self.response.write('</style>')

        else:
            # Normal als Modul aufgerufen
            self.templates.write("administation_menu", context_dict)

    #_________________________________________________________________________
    # install

    def install(self, package_name, module_name):
        """
        Modul in die DB eintragen
        """
        self.response.write(
            "<h3>Install %s.<strong>%s</strong></h3>" % (
                package_name, module_name
            )
        )
        data = Modules(self.request, self.response)
        data.installModule(module_name, package_name)

    def first_time_install(self, simulation=True):
        """
        Installiert alle wichtigen Module/Plugins
        Das sind alle Module, bei denen:
        "essential_buildin" == True oder "important_buildin" == True
        """
        self.response.write("<h2>First time install:</h2>\n")

        self._truncateTables()

        data = Modules(self.request, self.response)
        data.read_packages() # Nur die Plugins von Platte laden
        if debug:
            data.debug()

        data.first_time_install()

    def _truncateTables(self):
        self.response.write("<hr />\n")
        self.response.write(
            "<h4>truncate tables:</h4>\n"
            "<ul>\n"
        )
        tables = ("plugins", "plugindata", "pages_internal")
        for table in tables:
            self.response.write("\t<li>truncate table %s..." % table)

            try:
                self.db.cursor.execute("TRUNCATE TABLE $$%s" % table)
            except Exception, e:
                msg = (
                    "<h4>%s: %s</h4>"
                    "<h5>(Have you first init the tables?)</h5>"
                    "</li></ul>"
                ) % (sys.exc_info()[0], e)
                self.response.write(msg)
                return
            else:
                self.response.write("OK</li>\n")
        self.response.write("</ul>\n")
        self.response.write("<hr />\n")

    #_________________________________________________________________________
    # DEinstall

    def deinstall(self, id):
        """
        Modul aus der DB löschen
        """
        data = Modules(self.request, self.response)
        data.deinstallModule(id)

    #_________________________________________________________________________
    # reinit

    def reinit(self, id):
        """
        Modul wird deinstalliert und wieder installiert
        """
        data = Modules(self.request, self.response)
        data.reinit(id)

    #_________________________________________________________________________

    def activate(self, id):
        """
        Modul soll deaktiviert werden
        """
        data = Modules(self.request, self.response)
        data.activateModule(id)

    #_________________________________________________________________________

    def deactivate(self, id):
        """
        Modul soll deaktiviert werden
        """
        data = Modules(self.request, self.response)
        data.deactivateModule(id)

    #_________________________________________________________________________

    def debug_installed_modules_info(self, module_id):
        moduleData = Modules(self.request, self.response)
        moduleData.readAllModules()

        moduleData.debug()




















class InternalPage(object):
    """
    Alle Daten zusammenhängent mit der internenSeite
    """
    def __init__(self, request, response, package_dir_list, module_name, data):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = response.page_msg

        self.plugin_id = None
        self.method_id = None

        self.package_dir_list = package_dir_list
        self.module_name = module_name

        self.basePath = os.sep.join(self.package_dir_list)

        self.name = data["name"]

        self.data = data

    #_________________________________________________________________________

    def install(self, plugin_id, method_id):
        """
        Installiert die interne Seite mit zugehörigen CSS und JS Daten
        """
        self.plugin_id = plugin_id
        self.method_id = method_id

        msg = (
            "<li>install internal page '<strong>%s</strong>'...<ul>\n"
        ) % self.name
        self.response.write(msg)

        # Löscht eine evtl. verwaiste interne Seite:
        self.db.delete_internal_page(self.name)

        lastupdatetime_list = []

        html, lastupdatetime = self._getAdditionFiles("html", "HTML")
        lastupdatetime_list.append(lastupdatetime)

        css, lastupdatetime = self._getAdditionFiles("css", "StyleSheet")
        lastupdatetime_list.append(lastupdatetime)

        js, lastupdatetime = self._getAdditionFiles("js", "JavaScript")
        lastupdatetime_list.append(lastupdatetime)

        # Als Grundlage dient das neuste Datum
        lastupdatetime = max(lastupdatetime_list)

        # Hinweis: self.db übernimmt folgendes:
        # -template_engine und markup in IDs wandeln.
        # -createtime, lastupdateby eingetragen.
        internal_page = {
            "name"              : self.name,
            "plugin_id"         : self.plugin_id,
            "method_id"         : self.method_id,
            #~ "category"          : self.module_name,
            "description"       : self.data["description"],
            "content_html"      : html,
            "content_css"       : css,
            "content_js"        : js,
            "template_engine"   : self.data["template_engine"],
            "markup"            : self.data["markup"],
        }

        try:
            self.db.new_internal_page(internal_page, lastupdatetime)
        except Exception, e:
            raise IntegrityError(
                "Can't save new internal page to DB: %s - %s" % (
                    sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("</ul><li>internal page saved! OK</li>\n")

    def _getAdditionFiles(self, ext, name):
        filename = "%s/%s.%s" % (self.basePath, self.name, ext)
        if not os.path.isfile(filename):
            # Es gibt keine zusätzliche Datei ;)
            return "", 0

        msg = "<li>read '%s' %s..." % (filename, name)
        self.response.write(msg)
        try:
            lastupdatetime, content = self._getFiledata(filename)
        except Exception, e:
            self.response.write(
                "Error reading %s-File: %s</li>\n" % (
                    name, e
                )
            )
            return "", 0
        else:
            self.response.write("OK</li>\n")
            return content, lastupdatetime

    def _getFiledata(self, filename):
        try:
            lastupdatetime = os.stat(filename).st_mtime
        except:
            lastupdatetime = None

        f = file(filename, "rU")
        content = f.read()
        f.close()

        try:
            content = unicode(content, "utf8")
        except UnicodeError, e:
            self.response.write(
                "UnicodeError: Use 'replace' error handling..."
            )
            content = unicode(content, "utf8", errors='replace')

        return lastupdatetime, content

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("<strong>internal Page</strong> '%s':" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li>%s: %s</li>" % (k,v))
        self.page_msg("</ul>")






class Method(object):
    """
    Daten einer Methode von einem Module/Plugin
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = response.page_msg

        self.id = None # Method-ID
        self.plugin_id = None

    def add(self, package_dir_list, module_name, name):
        self.package_dir_list = package_dir_list
        self.module_name = module_name
        self.name = name

        self.data = {}

        # defaults
        self.internalPage = None
        self.data["must_login"] = True
        self.data["must_admin"] = True

    def add_from_DB(self, config):
        """
        Verarbeiten der Config beim einlesen des Plugins aus der DB
        """
        self.id = config["id"]
        self.plugin_id = config["plugin_id"]
        self.data.update(config)

    def assimilateConfig(self, config):
        """
        Verarbeiten der Config beim einlesen der Plugins von Platte
        """
        if 'internal_page_info' in config:
            internal_page_info = config['internal_page_info']

            # Eine interne Seite muß keinen speziellen Namen haben, dann nehmen
            # wir einfach den Namen der Methode:
            internal_page_info["name"] = internal_page_info.get(
                "name", self.name
            )

            self.internalPage = InternalPage(
                self.request, self.response,
                self.package_dir_list, self.name, internal_page_info
            )

        self.data.update(config)
        if 'internal_page_info' in config:
            # FIXME: Das ist scheiße, muß aber z.Z. gemacht werden:
            del(self.data['internal_page_info'])

    #_________________________________________________________________________

    def install(self, module_id):
        """
        Installiert Methode in die DB
        """
        msg = (
            "<li>install method '<strong>%s</strong>'..."
        ) % self.name
        self.response.write(msg)

        # methode in DB eintragen
        method_id = self.db.register_plugin_method(
            module_id, self.name, self.data
        )
        self.response.write("OK</li>\n")

        if self.internalPage != None:
            # zugehörige interne Seite in DB eintragen
            self.response.write('<li><ul class="install_ipages">\n')
            self.internalPage.install(module_id, method_id)
            self.response.write("</ul></li>\n")

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("Debug for method '<strong>%s</strong>':" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li>%s: %s</li>" % (k,v))
        if self.internalPage != None:
            self.internalPage.debug()
        self.page_msg("</ul>")








class Module(object):
    """
    Daten eines Modules
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.tools          = request.tools
        self.db             = request.db
        self.page_msg       = response.page_msg

    def add(self, name):
        self.name = name

        # defaults setzten:
        self.data = {
            "module_name": self.name,
            "installed": False,
            "active": False,
            "essential_buildin": False,
            "important_buildin": False,
        }
        self.methods = []

    def add_fromDisk(self, package_dir_list):
        self.data["config_name"] = "%s_cfg" % self.name
        self.data["package_dir_list"] = package_dir_list
        self.data["package_name"] = ".".join(package_dir_list)

        configObject = self._readConfigObject()
        self._assimilateConfig(configObject)
        self._setupMethods(configObject)
        self.data["version"] = self._getVersionInfo()

    def add_fromDB(self, RAWdict):
        self.data['package_name'] = package_dir_list = RAWdict['package_name']
        package_dir_list = package_dir_list.split("/")

        self.data["installed"] = True

        try:
            RAWdict = self.tools.filterDict(
                RAWdict,
                strKeys=[],
                intKeys=["id", "active"],
                defaults={
                    "version":"undefined",
                    "author":"undefined",
                    "description":"",
                    "url":"",
                    "SQL_deinstall_commands":None,
                }
            )
        except KeyError, e:
            raise KeyError, "Key %s not found in Module-RAWdict!" % e
        self.data.update(RAWdict)

        self.data["builtin"] = False

        if RAWdict["active"] == 0:
            self.data["active"] = False
        elif RAWdict["active"] == -1:
            self.data["builtin"] = True
            self.data["active"] = True
        elif RAWdict["active"] == 1:
            self.data["active"] = True

        module_id = self.data["id"]

        plugindata = self.db.get_plugindata(module_id)
        for method_data in plugindata:
            #~ print method_data
            method = Method(self.request, self.response)
            method.add(
                self.data['package_name'], self.name,
                method_data["method_name"]
            )
            method.add_from_DB(method_data)
            self.methods.append(method)

    #_________________________________________________________________________
    # Config-Daten von Platte lesen

    def _readConfigObject(self):
        """
        Liefert alle Daten zu einem Modul, aus der zugehörigen config-Datei.
        """
        package_dir_list = self.data["package_dir_list"][:] # Kopie der Liste
        package_dir_list.append(self.data["config_name"])
        packagePath = ".".join(package_dir_list)

        try:
            module_cfg_object = __import__(
                packagePath, {}, {}, [self.data["config_name"]]
            )
        except SyntaxError, e:
            raise SyntaxError("Can't import %s: %s" % (packagePath, e))
        else:
            return module_cfg_object

    def _getVersionInfo(self):
        package_dir_list = self.data["package_dir_list"]
        package_dir_list.append(self.name)
        packagePath = ".".join(package_dir_list)

        try:
            version = __import__(
                packagePath, {}, {}, [self.name]
            ).__version__
        except (ImportError, AttributeError):
            version = "[no __version__ set in Module %s]" % packagePath

        return version

    def _assimilateConfig(self, configObject):
        """
        Daten aus dem config-Objekt "speichern"
        """
        try:
            self.data["plugin_cfg"] = configObject.plugin_cfg
        except AttributeError:
            # Keine plugin_cfg vorhanden, ist auch ok ;)
            pass

        def getattrStriped(object, attr):
            result = getattr(object, attr)
            if type(result) == str:
                return result.strip()
            return result

        # Metadaten verarbeiten, die immer da sein müßen!
        keys = (
            "author", "url", "description", "long_description",
        )
        for key in keys:
            keyTag = "__%s__" % key
            try:
                self.data[key] = getattrStriped(configObject, keyTag)
            except AttributeError, e:
                msg = (
                    "Module/plugin config file '...%s' has no Entry for '%s'!"
                ) % (configObject.__file__[-35:], keyTag)
                raise AttributeError, msg

        # Optionale Einstellungsdaten
        self.data["module_manager_debug"] = getattr(
            configObject, "module_manager_debug", False
        )

        keys = (
            "SQL_install_commands", "SQL_deinstall_commands",
        )
        for key in keys:
            self.data[key] = getattr(configObject, key, None)

        keys = (
            "essential_buildin", "important_buildin"
        )
        for key in keys:
            keyTag = "__%s__" % key
            self.data[key] = getattr(configObject, keyTag, False)

    def _setupMethods(self, configObject):
        """
        Für jede Methoden des Plugins ein Objekt erstellen und in die Liste
        self.methods einfügen.
        """
        module_manager_data = configObject.module_manager_data
        for methodName, methodData in module_manager_data.iteritems():
            method = Method(self.request, self.response)
            method.add(self.data["package_dir_list"], self.name, methodName)
            method.assimilateConfig(methodData)
            self.methods.append(method)

    #_________________________________________________________________________

    def install(self, autoActivate=False):
        """
        Installiert das Modul und all seine Methoden
        """
        self.response.write("<h4>'%s'</h4>\n" % self.name)
        self.response.write(
            "\t<li>register Module '<strong>%s</strong>'..." % self.name
        )

        if autoActivate:
            self.data["active"] = True

        # Plugin Einstellungen
        self.data["plugin_cfg"] = self._get_plugin_cfg()

        # Modul in DB eintragen
        id = self.db.install_plugin(self.data)
        self.data["id"] = id
        self.response.write("OK</li>\n")

        self.response.write(
            '\t<li>register all Methodes:</li>\n'
            '\t<li><ul class="reg_methodes">\n'
        )
        # Alle Methoden in die DB eintragen
        for method in self.methods:
            method.install(id)

        self.response.write("\t</ul></li>\n")

    def _get_plugin_cfg(self):
        """
        plugin_cfg Daten
        """
        if not "plugin_cfg" in self.data:
            return None

        plugin_cfg_obj = plugin_cfg.PluginConfig(
            self.request, self.response,
            module_id=0,
            module_name = self.data["module_name"], method_name="[install]"
        )
        return plugin_cfg_obj.get_pickled_data(self.data["plugin_cfg"])

    def first_time_install(self):
        """
        installiert nur Module die wichtig sind
        """
        if self.data["essential_buildin"] or self.data["important_buildin"]:
            self.install(autoActivate=True)

    #_________________________________________________________________________

    def deinstall(self):
        plugin_id = self.data["id"]

        self.page_msg(
            "delete Module '%s' (id %s) in database." % (self.name, plugin_id)
        )

        # Alle internen Seiten löschen
        page_names = self.db.delete_internal_page_by_plugin_id(plugin_id)
        if page_names != []:
            self.page_msg("Internal pages %s deleted" % page_names)

        # Alle Methonden aus DB-Tabelle 'plugindata' löschen
        self.db.delete_plugindata(plugin_id)

        # Plugin selber aus DB-Tabelle 'plugins' löschen
        self.db.delete_plugin(plugin_id)

    def activate(self):
        self.page_msg("activate Module '%s' in database..." % self.name)
        self.db.activate_module(self.data["id"])

    def deactivate(self):
        self.page_msg("deactivate Module '%s' in database..." % self.name)
        self.db.deactivate_module(self.data["id"])

    #_________________________________________________________________________

    def getData(self):
        return self.data

    #_________________________________________________________________________

    def __repr__(self):
        return "<...self.Module '%s' object, \nData: %s\n>" % (
            self.name, self.data
        )
    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("Module '<strong>%s</strong>' debug:" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li><em>%s</em>: %s</li>" % (k,v))
        for method in self.methods:
            method.debug()
        self.page_msg("</ul>")






class Modules(object):
    """
    Daten aller Module
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = response.page_msg

        self.data = {}

        try:
            self.isadmin = self.request.session.get("isadmin", False)
        except AttributeError:
            # In der install Sektion gibts keine Session
            self.isadmin = False

    def readAllModules(self):
        self._get_from_db()
        self.read_packages()

    def addModule(self, module_name, package_dir_list):
        if module_name in self.data:
            # Daten sind schon aus der DB da.
            return

        module = Module(self.request, self.response)
        module.add(module_name)
        module.add_fromDisk(package_dir_list)
        self.data[module_name] = module

    def addModule_fromDB(self, moduledata):
        module_name = moduledata["module_name"]
        module = Module(self.request, self.response)
        module.add(module_name)
        module.add_fromDB(moduledata)
        self.data[module_name] = module

    #_________________________________________________________________________

    def getModuleStatusList(self):
        "Liste alle vorhandenden Module"
        result = []
        for module_name, moduleData in self.data.iteritems():
            data = moduleData.getData()
            result.append(data)

        return result

    #_________________________________________________________________________

    def read_packages(self):
        """
        Alle verfügbaren packages durch scannen.
        """
        for package in available_packages:
            self._read_one_package(package)

    def _read_one_package(self, package_name):
        """
        Dateiliste eines packages erstellen.
        """
        packageDir = os.path.join(package_basedir, package_name)
        for item in os.listdir(packageDir):
            itemDir = os.path.join(package_basedir, package_name, item)

            if not os.path.isdir(itemDir):
                continue

            init = os.path.join(itemDir, "__init__.py")
            if not os.path.isfile(init):
                # Verz. hat keine init-Datei
                continue

            module_cfg = os.path.join(itemDir, "%s_cfg.py" % item)
            if not os.path.isfile(module_cfg):
                # Kein Config-Datei vorhanden -> kein PyLucid-Module
                continue

            module = os.path.join(itemDir, "%s.py" % item)
            if not os.path.isfile(module):
                continue

            if self.isadmin:
                self.addModule(
                    module_name = item,
                    package_dir_list = [package_basedir, package_name, item]
                )
            else:
                try:
                    self.addModule(
                        module_name = item,
                        package_dir_list = [
                            package_basedir, package_name, item
                        ]
                    )
                except Exception, e:
                    self.page_msg(
                        "Can't use Module %s.%s - Error: %s" % (
                            package_basedir, package_name, e
                        )
                    )

    #_________________________________________________________________________
    # install

    def installModule(self, module_name, package_name):
        """
        Installieren eines bestimmten Modules/Plugins
        """
        package_name = package_name.split(".")
        self.addModule(module_name, package_name)

        module = self.data[module_name]
        module.install()

    def first_time_install(self):
        """
        Alle wichtigen Module installieren
        """
        self.response.write(
            "<h3>install all essential and important buildin plugins</h3>"
        )
        try:
            for module_name, module in self.data.iteritems():
                self.response.write('<ul class="module_install">\n')
                module.first_time_install()
                self.response.write('</ul>\n')
        except IntegrityError, e:
            msg = (
                "install all modules failed!"
                " make DB rollback"
                " Error: %s"
            ) % e
            self.response.write(msg)
            try:
                self.db.rollback()
            except Exception, e:
                self.response.write("Can't make rollback: %s" % e)
        else:
            self.db.commit()

    #_________________________________________________________________________

    def deinstallModule(self, id):
        """
        Löscht das Module/Plugin mit der angegebenen ID
        """
        #~ self.page_msg("Deinstall module with id:", id)
        module = self.getModule(id)
        module.deinstall()

    #_________________________________________________________________________

    def reinit(self, id):
        module = self.getModule(id)
        module_name = module.data["module_name"]
        package_name = module.data["package_name"]

        #~ self.page_msg("reinit not implemented yet!")

        self.deinstallModule(id)
        #~ module.deinstall()
        del(self.data[module_name])

        self.installModule(module_name, package_name)

        module = self.data[module_name]
        id = module.data["id"]

        self.activateModule(id)

    #_________________________________________________________________________

    def getModule(self, id):
        # FIXME: sollte Prüfen ob das Modul nicht schon von der DB geladen ist!
        RAWdict = self.db.get_plugin_data_by_id(id)
        self.addModule_fromDB(RAWdict)

        module = self.data[RAWdict["module_name"]]
        return module

    #_________________________________________________________________________

    def activateModule(self, id):
        #~ self.page_msg("activate module with id:", id)
        module = self.getModule(id)
        module.activate()

    def deactivateModule(self, id):
        #~ self.page_msg("deactivate module with id:", id)
        module = self.getModule(id)
        module.deactivate()

    #_________________________________________________________________________
    # Informationen über in der DB installierte Module / Plugins

    def _get_from_db(self):
        try:
            installed_modules_info = self.db.get_installed_modules_info()
        except Exception, e:
            self.response.write(
                "<h1>Can't get installed module data from DB:</h1>"
            )
            self.response.write("<h4>%s</h4>" % e)
            self.response.write("<h3>Did you run install_PyLucid.py ???</h3>")
            raise #FIXME!
        for moduleData in installed_modules_info:
            self.addModule_fromDB(moduleData)

    #_________________________________________________________________________
    # Debug

    def debug(self):
        self.page_msg("Module Debug:")
        oldPageMsgRaw = self.page_msg.raw
        self.page_msg.raw = True

        self.page_msg("<ul>")
        for module_name, module in self.data.iteritems():
            self.page_msg("<li>%s:" % module_name)
            module.debug()
            self.page_msg("</li>")
        self.page_msg("</ul>")

        self.page_msg.raw = oldPageMsgRaw







