#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import sys

class out_buffer(object):
    """
    Hilfsklasse um Ausgaben erst zwischen zu speichern und dann gesammelt zu
    erhalten.
    stderr_obj ist PyLucid's self.request.page_msg ;)

    bsp.:
    from PyLucid.tools.out_buffer import out_buffer
    out = out_buffer(self.page_msg)
    out.write("BlaBla")
    out("Noch was...")
    self.page_msg("Ausgaben waren:", out.get())
    """
    def __init__(self, stderr_obj):
        self.stderr_obj = stderr_obj

        self.data = []
        #~ self.sep = "\n"

    #~ def set_sep(self, sep):
        #~ self.sep = sep

    def write(self, *txt):
        for i in txt:
            if isinstance(i, str):
                try:
                    i = unicode(i, encoding="utf-8")
                except UnicodeError, e:
                    self.stderr_obj("UnicodeError:", e)
                    i = unicode(i, encoding="utf-8", errors="replace")
            self.data.append(i)

    def __call__(self, *txt):
        self.write(*txt)

    def get(self):
        out_data = "".join(self.data)
        self.data = []
        return out_data

    def flush(self):
        return


class Redirector(object):
    """
    Nutzt den out_buffer und speichert alle stdout und stderr Ausgaben.
    stderr_obj kann z.B. "self.page_msg" sein ;)
    """
    def __init__(self, stderr_obj):
        self.oldout = sys.stdout
        self.olderr = sys.stderr

        self.out_buffer = out_buffer(stderr_obj)
        sys.stdout = self.out_buffer
        sys.stderr = self.out_buffer

    def get(self):
        sys.stdout = self.oldout
        sys.stderr = self.olderr
        return self.out_buffer.get()