#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Menü Generator für Colubrid's Oject-Application
"""

__version__ = "v0.1.0"

__history__ = """
v0.1
    - erste Version
"""


import cgi, posixpath



class ObjectApp_MenuGenerator(object):

    def __init__(self, response, root, base_path = "", blacklist=[]):
        self.response = response
        self.root = root
        self.base_path = base_path.lstrip("/")
        self.blacklist = blacklist

    def root_link(self, path, info):
        "Methode zum überscheiben"
        self.response.write('<a href="%s">%s</a>' % (path, info))

    def sub_link(self, path, info):
        "Methode zum überscheiben"

        self.response.write('<a href="%s">%s</a>' % (path, info))

    def _get_objnamelist(self, obj, attr_type):
        """
        Baut eine Liste mit den nötigen Informationen für ein Menü zusammen
        Hilfmethode für make_menu
        """
        result = []
        for objname in dir(obj):
            #~ self.response.echo(objname)
            if objname.startswith("_") or objname in self.blacklist:
                continue

            obj_attr = getattr(obj, objname)

            if attr_type == "methods": # Methoden einer Klasse
                if getattr(obj_attr, "__call__", None) == None:
                    continue
            elif attr_type == "class": # Klassen des root-Objekts
                if type(obj_attr) != type:
                    continue
            else:
                raise TypeError("attr_type must be 'class' or 'methods'!")

            if obj_attr.__doc__:
                info = obj_attr.__doc__
                info = info.strip().split("\n",1)[0]
            else:
                info = objname

            info = cgi.escape(info)

            result.append([info, objname, obj_attr])
        result.sort()
        return result

    def get_menu_data(self):
        """ Liefert eine verschachtelre Liste mit den Menüdaten zurück """
        result = []
        objnamelist = self._get_objnamelist(self.root, attr_type="class")
        for info, path, obj_attr in objnamelist:
            path = posixpath.join(self.base_path, path)
            result.append((path, info))
            temp = []
            subobjnamelist = self._get_objnamelist(obj_attr, attr_type="methods")
            for sub_info, sub_path, _ in subobjnamelist:
                sub_path = "/%s/%s/" % (path, sub_path)
                temp.append((sub_path, sub_info))
            result.append(temp)
        return result

    # Zum überschreiben/Anpassen:
    root_list_tags = ('\n<ul>\n', '</ul>\n', '\t<li>', '</li>\n')
    sub_list_tags = ('\t<ul>\n', '\t</ul>\n', '\t\t<li>', '</li>\n')

    def make_menu(self):
        """
        Generiert ein Menü für alle vorhandenen Objekte/Pfade und nutzt
        dabei die erste Zeile des DocString von jeder Klasse/Methode.
        Generell wird das Menü nach DocString sortiert, d.h. wenn man
        gezielt eine sortierung haben will, kann man z.B. den DocString
        mit 1., 2., 3. anfangen.
        """
        def write_menu(handler, item, tags):
            """Ruft den passenden Handler, also self.sub_link oder
            self.root_link mit den Menü-Daten auf"""
            self.response.write(tags[2])
            handler(*item)
            self.response.write(tags[3])

        self.response.write(self.root_list_tags[0])
        for item in self.get_menu_data():
            if isinstance(item, list):
                # Untermenüpunkte
                self.response.write(self.root_list_tags[2])
                self.response.write(self.sub_list_tags[0])
                for sub_item in item:
                    write_menu(self.sub_link, sub_item, self.sub_list_tags)
                self.response.write(self.sub_list_tags[1])
                self.response.write(self.root_list_tags[3])
            else:
                # Hauptmenüpunkt
                write_menu(
                    self.root_link, item, self.root_list_tags
                )

        self.response.write(self.root_list_tags[1])