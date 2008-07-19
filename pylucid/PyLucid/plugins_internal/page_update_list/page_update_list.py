# -*- coding: utf-8 -*-

"""
    PyLucid page update list plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a list of the latest page updates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev$"

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page

class page_update_list(PyLucidBasePlugin):

    def lucidTag(self, count=10):
        try:
            count = int(count)
        except Exception, e:
            msg = "page_update_list error: count must be a integer (%s)" % e
            self.page_msg.red(msg)
            self.response.write("[%s]" % msg)
            return

        if self.request.user.is_staff:
            hide_non_public = False
        else:
            hide_non_public = True

        page_updates = Page.objects.get_update_info(hide_non_public)
        page_updates = page_updates[:count]

        context = {"page_updates": page_updates}

        self._render_template("PageUpdateTable", context)#, debug=True)

