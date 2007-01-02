#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
self.request.L10N

nutzt Tabelle "l10n"

Zugriff als Dict, abhängig von der aktuellen Sprache.

Die Sprachen werden abgekürzt, Sprachenkürzeln nach ISO 639-1
siehe http://www.python-forum.de/topic-8625.html


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

import UserDict

from PyLucid.system.exceptions import *


class L10N(object):
    cache = {}

    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # shorthands
        #~ self.runlevel       = request.runlevel
        #~ self.session        = request.session
        #~ self.preferences    = request.preferences
        #~ self.URLs           = request.URLs
        #~ self.log            = request.log
        #~ self.module_manager = request.module_manager
        #~ self.tools          = request.tools
        #~ self.render         = request.render
        #~ self.tag_parser     = request.tag_parser
        #~ self.staticTags     = request.staticTags
        #~ self.templates      = request.templates

        self.page_msg       = response.page_msg
        self.db             = request.db
        self.i18n           = request.i18n

    def get(self, key):
        """
        Wert zum key direkt in der aktuellen Sprache
        """
        try:
            return self.cache[self.i18n.current_lang][key]
        except KeyError:
            # Der Wert wurde evtl. noch nicht von der DB geholt
            try:
                value = self.db.get_L10N(self.i18n.current_lang, key)
            except KeyError:
                if not self.i18n.current_lang in self.cache:
                    raise KeyError("l10n Error: Language '%s' unknwon." % lang)
                else:
                    msg = (
                        "l10n Error:"
                        " Key '%s' for Language '%s' not defined."
                    ) % (key, lang)
                    raise KeyError(msg)

        # Für späteren Zugriff cachen
        if not self.i18n.current_lang in self.cache:
            self.cache[self.i18n.current_lang] = {}
        self.cache[self.i18n.current_lang][key] = value

        return value

    #~ def set(self, key, value):
        #~ """
        #~ Setzt einen Wert für die aktuelle Sprache
        #~ """
        #~ self.cache[lang][key] = value
        #~ self.db.update()

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("L10N_data - Debug:")
        self.page_msg("-"*30)
        for k,v in self.cache.iteritems():
            self.page_msg("%s - %s" % (k,cgi.escape(repr(v))))
        self.page_msg("-"*30)





