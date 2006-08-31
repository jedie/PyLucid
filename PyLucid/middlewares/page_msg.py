#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware

Speichert Nachrichten die in der Seite angezeigt werden sollen
Wird am Ende des Reuqestes durch ein Replace Middleware in die
Seite eingesetzt.
"""


__version__="0.2"

__history__="""
v0.2
    - used pprint for dicts and lists
v0.1
    - init
"""

import cgi, pprint


class page_msg_Container(object):
    """
    Kleine Klasse um die Seiten-Nachrichten zu verwalten
    page_msg wird in index.py den PyLucid-Objekten hinzugefugt.
    mit PyLucid["page_msg"]("Eine neue Nachrichtenzeile") wird Zeile
    für Zeile Nachrichten eingefügt.
    Die Nachrichten werden ganz zum Schluß in der index.py in die
    generierten Seite eingeblendet. Dazu dient der Tag <lucidTag:page_msg/>

    self.raw - Für Ausgaben ohne <br />

    """
    def __init__(self, debug = False):
        self.raw = False
        self.debug = debug
        self.data = ""

    def __call__(self, *msg):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        if self.raw:
            self.add_data(
                "%s\n" % " ".join([str(i) for i in msg])
            )
            return

        if self.debug:
            try:
                import inspect
                # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
                stack = inspect.stack()[1]
                filename = stack[1].split("/")[-1][-20:]
                fileinfo = "%-20s line %3s: " % (filename, stack[2])
                self.data += fileinfo.replace(" ","&nbsp;")
            except Exception, e:
                self.data += "<small>(inspect Error: %s)</small> " % e

        for item in msg:
            if isinstance(item, dict) or isinstance(item, list):
                item = pprint.pformat(item)
                item = item.split("\n")
                for line in item:
                    line = cgi.escape(line)
                    line = line.replace(" ","&nbsp;")
                    self.add_data("%s<br />\n" % line)
            else:
                self.add_data(item)
                self.data += " "

        self.data += "<br />\n"

    def add_data(self, txt):
        # FIXME: Das ist mehr schlecht als recht... Die Behandlung von unicode
        # muß irgendwie anders gehen!
        if isinstance(txt, unicode):
            txt = txt.encode("UTF-8", "replace")
        self.data += str(txt)

    def write(self, *msg):
        self.__call__(*msg)

    def get(self):
        if self.data != "":
            # Nachricht vorhanden -> wird eingeblendet
            return (
                '\n<fieldset id="page_msg"><legend>page message</legend>\n'
                '%s'
                '\n</fieldset>'
            ) % self.data
        else:
            return ""



class page_msg(object):
    """
    Fügt in's environ das page_msg-Objekt hinzu
    """
    def __init__(self, app, debug):
        self.app = app
        self.debug = debug

    def __call__(self, environ, start_response):
        environ['PyLucid.page_msg'] = page_msg_Container(self.debug)
        return self.app(environ, start_response)

