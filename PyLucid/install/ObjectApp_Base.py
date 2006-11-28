#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
BasisMethoden für alle Install-App-Bereiche
"""


# Imports für ObjectApp_Base-Klasse
import inspect, sys, posixpath





class ObjectApp_Base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """

    def _get_module_admin(self):
        from PyLucid.modules.module_admin.module_admin import module_admin

        module_admin = module_admin(self.request, self.response)

        return module_admin


    def _execute(self, title, SQLcommand, args=()):
        self.response.write("<h4>%s:</h4>\n" % title)
        self.response.write("<pre>\n")

        try:
            self._db.cursor.execute(SQLcommand, args)
        except Exception, e:
            self.response.write("ERROR: %s" % e)
        else:
            self.response.write("OK")

        self.response.write("</pre>\n")

    #_________________________________________________________________________

    def _write_info(self):
        try:
            stack_info = inspect.stack()
            #~ self.response.echo(stack_info)
            stack_info = stack_info[1]
            attr_name = stack_info[3]
            info = getattr(self, attr_name).__doc__
            info = info.strip().split("\n",1)[0]
        except:
            info = self.request.environ['PATH_INFO']

        self.response.write("<h3>%s</h3>" % info)

        self._write_backlink()

    def _write_backlink(self):
        url = self._URLs.installBaseLink()
        self.response.write('<p><a href="%s">menu</a></p>' % url)

    def _confirm(self, txt, simulationCheckbox=False):
        """
        Automatische Bestätigung
        """
        if "simulation" in self.request.form:
            # Ist ja nur als String enthalten, wir wandeln das in
            # ein echtes True:
            self.request.form["simulation"] = True

        if "confirm" in self.request.form:
            # confirm-POST-Form wurde schon bestätigt
            return True

        self.response.write("<h4>%s</h4>\n" % txt)


        url = self._URLs.currentAction()
        self.response.write(
            '<form name="confirm" method="post" action="%s">\n' % url
        )

        if simulationCheckbox:
            self.response.write(
                '\t<label for="simulation">Simulation only:</label>\n'
                '\t<input id="simulation" name="simulation"'
                ' type="checkbox" value="True" checked="checked" />\n'
                '\t<br />\n'
            )

        self.response.write(
            '\t<input type="submit" value="confirm" name="confirm" />\n'
            '</form>\n'
        )

        # Es soll erst weiter gehen, wenn das Formular bestätigt wurde:
        sys.exit(0)

    #_________________________________________________________________________
    ## Sub-Action

    def _autoSubAction(self, subactions, current_action):
        self._write_subactionmenu(subactions, current_action)
        if current_action == None:
            return

        if not isinstance(current_action, basestring):
            self.response.write("TypeError!")
            return

        if not hasattr(self, current_action):
            self.response.write("Error: %s not exists!" % current_action)
            return

        action = getattr(self, current_action)
        action()

    def _write_subactionmenu(self, subactions, current_action):
        self.response.write("<p>Please select:</p>\n")
        self.response.write("<ul>\n")
        for action in subactions:
            if not hasattr(self, action):
                self.response.write("Error: %s not exists!" % action)
                continue

            name = self._nicecurrent_action(action)
            if current_action == action:
                name = "<strong>%s</strong>" % name

            url = self._URLs.installSubAction(action)
            txt = (
                '\t<li>'
                '<a href="%s">%s</a>'
                '</li>\n'
            ) % (url, name)
            self.response.write(txt)
        self.response.write("</ul>\n")

    def _nicecurrent_action(self, current_action):
        current_action = current_action.strip("_")
        current_action = current_action.replace("_", " ")
        return current_action


    #~ def _currentActionLink(self):
        #~ return self._URLs["action"]








