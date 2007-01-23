#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""

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

__version__= "$Rev:$"

#~ debug = True
debug = False

from PyLucid.system.BaseModule import PyLucidBaseModule

class ModuleSetup(PyLucidBaseModule):
    def module_setup(self, function_info):
        """
        built a simple select menu, from all modules/plugins how has a setup
        method.
        """
        if function_info!=None:
            # Ein Modul wurde ausgewählt
            try:
                module_id = int(function_info[0])
            except (KeyError, ValueError):
                self.page_msg("URL Error!")
            else:
                self.setup_module(module_id)
            return

        setup_methods = self.db.get_setup_methods()

        for module in setup_methods:
            module["url"] = self.URLs.currentAction(module["id"])

        context = {
            "modules": setup_methods,
        }
        self.templates.write("module_setup", context, debug)

    def setup_module(self, module_id):
        """
        run the setup method for the selected module/plugin
        """
        module_name = self.db.get_plugin_data_by_id(
            module_id, select_items=["module_name"]
        )["module_name"]

        self.module_manager.run_direkt(module_name, "setup")
