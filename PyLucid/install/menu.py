#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Menu Routinen für "install PyLucid"
"""


from PyLucid.install.ObjectApp_MenuGenerator import ObjectApp_MenuGenerator
from PyLucid.install.ObjectApp_Base import ObjectApp_Base

info_links = """
<hr />
Info at pylucid.org:
<a href="http://www.pylucid.org/index.py/InstallPyLucid/">
how to install PyLucid
</a>
|
<a href="http://www.pylucid.org/index.py/UpdateInstructions/">
update instructions
</a>
"""

class Install_MenuGenerator(ObjectApp_MenuGenerator):
    """
    Anpassen des Menügenerators
    """
    # id="menu" in ul einbauen
    root_list_tags = ('\n<ul id="menu">\n', '</ul>\n', '\t<li>', '</li>\n')

    def root_link(self, path, info):
        "Methode zum Überscheiben"
        try: # Zahlen bei den Hauptmenüpunkten weg schneiden
            info = info.split(" ",1)[1]
        except:
            pass
        self.response.write('<h4>%s</h4>' % info)


class menu(ObjectApp_Base):
    def index(self):
        "Main Menu"
        self.response.write("Please select:")
        self.MenuGenerator.make_menu()

        self.response.write(info_links)

    #~ def name(self, arg1="Default", arg2="Default"):
        #~ """Beispiel für eine Parameter übergabe"""
        #~ self._info('index.name')
        #~ self.response.write(
            #~ 'arg1="%s" - arg2="%s"' % (arg1, arg2)
        #~ )