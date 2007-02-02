#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
Füllt ins Template die eigentliche Seite oder das Ergebnis
eines Plugins/Kommandos.

<lucidTag:page_body/>
"""

__version__="0.1"

__history__="""
v0.1
    - Neu: seid PyLucid v0.7
"""

__todo__ = """
"""

# Python-Basis Module einbinden
#~ import



from PyLucid.system.BaseModule import PyLucidBaseModule

class page_body(PyLucidBaseModule):

    def lucidTag( self ):
        #~ if self.request.runlevel == "command":
            #~ self.command_content()
        #~ else:
            #~ self.normal_page()

    #~ def command_content(self):
        #~ self.module_manager.run_command()
        #~ if self.session.has_key("render follow"):
            #~ self.normal_page()
            #~ # Soll nur einmal zählen:
            #~ del(self.session["render follow"])

    #~ def normal_page(self):
        page_id = self.session["page_id"]
        content = self.render.get_rendered_page(page_id)
        #~ self.page_msg("id",page_id,"content:", content)
        self.response.write(content)

