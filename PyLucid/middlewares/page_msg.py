#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware

Speichert Nachrichten die in der Seite angezeigt werden sollen
Wird am Ende des Reuqestes durch ein Replace Middleware in die
Seite eingesetzt.
"""


__version__="0.3"

__history__="""
v0.3
    - self.data ist nun eine Liste und wird per "".join() am Ende verarbeitet
    - Es gibt nun Farbige ausgaben!
v0.2
    - used pprint for dicts and lists
v0.1
    - init
"""

__ToDo__ = """
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
        self.debug_mode = debug
        self.data = []

    #_________________________________________________________________________

    def write(self, *msg):
        self.append_color_data("blue", *msg)

    def __call__(self, *msg):
        """ Alte Methode um Daten "auszugeben", Text ist dann schwarz """
        self.append_color_data("blue", *msg)

    def debug(self, *msg):
        self.append_color_data("gray", *msg)

    def black(self, *msg):
        self.append_color_data("black", *msg)

    def green(self, *msg):
        self.append_color_data("green", *msg)

    def red(self, *msg):
        self.append_color_data("red", *msg)

    #_________________________________________________________________________

    def append_color_data(self, color, *msg):
        self.data.append('<span style="color:%s;">\n' % color)
        self.append_data(*msg)
        self.data.append('</span>\n')

    def append_data(self, *msg):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        if self.raw:
            self.encode_and_append_data(
                "%s\n" % " ".join([str(i) for i in msg])
            )
            return

        if self.debug_mode:
            # Datei, Zeilennummer, aus dem die Nachricht stammt, anzeigen
            try:
                import inspect
                for stack_frame in inspect.stack():
                    # Im stack vorwärts gehen, bis außerhalb dieser Datei
                    filename = stack_frame[1]
                    if filename.rsplit("/",1)[1] != "page_msg.py":
                        lineno = stack_frame[2]
                        break

                filename = "...%s" % filename[-20:]
                fileinfo = "%-20s line %3s: " % (filename, lineno)
                self.data.append(fileinfo.replace(" ","&nbsp;"))
            except Exception, e:
                self.data.append("<small>(inspect Error: %s)</small> " % e)

        for item in msg:
            if isinstance(item, dict) or isinstance(item, list):
                item = pprint.pformat(item)
                item = item.split("\n")
                for line in item:
                    line = cgi.escape(line)
                    line = line.replace(" ","&nbsp;")
                    self.encode_and_append_data("%s<br />\n" % line)
            else:
                self.encode_and_append_data(item)
                self.data.append(" ")

        self.data.append("<br />\n")

    def encode_and_append_data(self, txt):
        # FIXME: Das ist mehr schlecht als recht... Die Behandlung von unicode
        # muß irgendwie anders gehen!
        if isinstance(txt, unicode):
            txt = txt.encode("UTF-8", "replace")
        self.data.append(str(txt))

    #_________________________________________________________________________

    def get(self):
        if self.data != []:
            # Nachricht vorhanden -> wird eingeblendet
            return (
                '\n<fieldset id="page_msg"><legend>page message</legend>\n'
                '%s'
                '\n</fieldset>'
            ) % "".join(self.data)
        else:
            return ""



class page_msg(object):
    """
    Fügt in's environ das page_msg-Objekt hinzu
    """
    def __init__(self, app, debug):
        self.app = app
        self.debug_mode = debug

    def __call__(self, environ, start_response):
        environ['PyLucid.page_msg'] = page_msg_Container(self.debug_mode)
        return self.app(environ, start_response)

