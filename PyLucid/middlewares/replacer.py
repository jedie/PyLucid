#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Middelware um Tags in den
Ausgaben zu ersetzten.

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

import time, re


init_clock = time.clock()

page_msg_tag        = "<lucidTag:page_msg/>"
script_duration_tag = "<lucidTag:script_duration/>"
# Fängt an mit PyLucid und nicht mit lucid, weil der Tag ansonsten durch
# RE im PyLucid-Response-Objekt ersetzt wird!
add_code_tag        = "<PyLucidInternal:addCode/>"



class Replacer(object):
    def __init__(self, app):
        self.app = app

    def replace_script_duration(self, line, environ):
        request_time = time.time() - environ["request_start"]
        overall_clock = time.clock() - init_clock

        time_string = "%.2fSec. - %.2foverall" % (
            request_time, overall_clock
        )

        line = line.replace(script_duration_tag, "%s" % time_string)

        return line

    def replace_page_msg(self, line, environ):
        page_msg = environ['PyLucid.page_msg']

        line = line.replace(page_msg_tag, page_msg.get())
        return line

    def addCode(self, line, environ):
        code = environ['PyLucid.addCode']
        code = code.get()

        line = line.replace(add_code_tag, code)
        return line


    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))

        for line in result:
            if script_duration_tag in line:
                line = self.replace_script_duration(line, environ)

            if page_msg_tag in line:
                line = self.replace_page_msg(line, environ)

            if add_code_tag in line:
                line = self.addCode(line, environ)

            yield line

        if hasattr(result, 'close'):
            result.close()



class AddCode(object):
    tag = add_code_tag

    def __init__(self, app):
        self.app = app
        self.data = []
        self.ids = []

    def get(self):
        data = "".join(self.data)
        self.data = []
        return data

    def insert(self, code):
        code = self._encode(code)
        self.data.insert(0, code)

    def add(self, code, id):
        if id in self.ids:
            # Wurde schon einmal hinzugefügt
            return

        code = self._encode(code)
        self.data.append(code)
        self.ids.append(id)

    def _encode(self, code):
        if not isinstance(code, unicode):
            return code

        try:
            return code.encode("utf8")
        except UnicodeError, e:
            # Fehler sollte ausgegeben werden, aber wohin???
            # Evtl. in die SQL-Log Tabelle???
            return data.encode("utf8", "replace")

    def __call__(self, environ, start_response):
        environ['PyLucid.addCode'] = self
        return self.app(environ, start_response)















