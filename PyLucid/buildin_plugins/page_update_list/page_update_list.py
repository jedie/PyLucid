#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:page_update_list />
oder
<lucidFunction:page_update_list>20</lucidFunction>
Generiert eine Liste der "letzten Änderungen"

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



from PyLucid.system.BaseModule import PyLucidBaseModule


class page_update_list(PyLucidBaseModule):

    def lucidTag(self):
        self.write_list(10)

    def lucidFunction(self, function_info=10):
        try:
            count = int(function_info)
        except Exception, e:
            msg = "lucidFunction is not a int number: %s" % e
            self.page_msg(msg)
            return "[%s]" % msg

        self.write_list(count)

    def write_list(self, count):
        page_updates = self.db.get_page_update_info(10)

        context = {
            "page_updates" : page_updates
        }
        #~ self.page_msg(context)

        self.templates.write("PageUpdateTable", context)













