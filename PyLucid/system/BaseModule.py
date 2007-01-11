#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Basis Modul von den andere Module erben können

Bsp.:

from PyLucid.system.BaseModule import PyLucidBaseModule

class Bsp(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(Bsp, self).__init__(*args, **kwargs)



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



from PyLucid.system.exceptions import *


class PyLucidBaseModule(object):

    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # shorthands
        self.runlevel       = request.runlevel
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.log            = request.log
        self.module_manager = request.module_manager
        self.tools          = request.tools
        self.render         = request.render
        self.staticTags     = request.staticTags
        self.templates      = request.templates

        try:
            self.plugin_cfg = request.plugin_cfg
            self.i18n       = request.i18n
            self.l10n       = request.l10n
        except AttributeError:
            # Im _install Bereich sind diese Objekte nicht verfügbar
            pass

        self.page_msg       = response.page_msg

        self.environ        = request.environ

    def debug(self):
        """
        Aktiviert colobrid's debug-Ausgabe in die page_msg rein.
        """
        self.response.debug()
