#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Benutzerverwalung für secure-MD5-JavaScript login

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

__version__ = "$Rev$"

__todo__ = """
    - Warum nicht das Template "user_table.html" und "add_user.html" direkt
        zusammenlegen???
"""


# Standart Python Module
import cgitb;cgitb.enable()
import os, sys, cgi, md5


# eigene Module
from PyLucid.system import crypt

from PyLucid.system.exceptions import *
from PyLucid.system.BaseModule import PyLucidBaseModule


#~ debug = True
debug = False


class userhandling(PyLucidBaseModule):
    """
    Verwaltung von Userdaten in der DB
    """
    def __init__(self, *args, **kwargs):
        super(userhandling, self).__init__(*args, **kwargs)

        # Damit beim installieren internal_pages direkt von Platte gelesen
        # werden können, muß der Pfad angegeben werden:
        self.templates.template_path = ["PyLucid","modules","userhandling"]

    def manage_user(self):
        """ Verwaltung von Usern """
        if debug:
            self.page_msg(self.request.form)

        additional_context=None

        if "add user" in self.request.form:
            # Es wurde das Formular abgeschickt
            self.add_user_action()
        elif "save" in self.request.form:
            self.save_changes()
        elif "delete" in self.request.form:
            self.delete_user()
        elif "details" in self.request.form:
            additional_context = {"user_details": self.user_details()}
        elif "new password" in self.request.form:
            self.new_password_form()
        elif "md5pass" in self.request.form:
            self.set_new_password()

        self.write_userlist_page(additional_context)

    def write_userlist_page(self, additional_context=None):
        context = {
            "url": self.URLs.currentAction()
        }

        if additional_context:
            context.update(additional_context)

        ## User Tabelle
        select_items = ["id","name","realname","email","admin"]
        user_list = self.db.get_all_userdata(select_items)
        context["user_list"] = user_list
        if debug:
            self.page_msg(context)
        self.templates.write("user_table", context)

        ## neuer User Form
        # Bei _install soll i.d.R. ein admin erstellt werden, deswegen soll
        # der Admin-Button "checked" sein
        if self.runlevel.is_install():
            context["runlevel_is_install"] = True
        else:
            context["runlevel_is_install"] = False

        #~ self.page_msg(context)
        self.templates.write("add_user", context)


    def save_changes(self):
        try:
            id = self.request.form["id"]
            name = self.request.form["name"]
            email = self.request.form["email"]
        except KeyError, e:
            msg = (
                "Formular Error: Key '%s' not found!\n"
                "No User added."
            ) % e
            self.page_msg(msg)
            return

        realname = self.request.form.get("realname","")
        admin = self.request.form.get("admin", 0)

        try:
            self.db.update_userdata(id, name, realname, email, admin)
        except Exception, e:
            msg = "Error saving user data (id: %s): %s" % (id, e)
        else:
            msg = "Data from user '%s' saved!" % name

        self.page_msg(msg)

    def add_user_action(self):
        """
        Verarbeitet ein abgeschicktes "add_user" Formular
        """
        try:
            username = self.request.form["username"]
            email = self.request.form["email"]
        except KeyError, e:
            msg = (
                "Formular Error: Key '%s' not found!\n"
                "No User added."
            ) % e
            self.page_msg(msg)
            return

        realname = self.request.form.get("realname","")
        is_admin = self.request.form.get("is_admin", False)

        try:
            user_id = self.db.add_new_user(
                username, realname, email, is_admin
            )
        except Exception, e:
            self.page_msg("Can't insert user! (%s)\n" % e)
            return

        self.page_msg.green("User '%s' added." % username)
        self.page_msg("Please set a new password.")

        self.new_password_form(user_id)


    def delete_user(self):
        try:
            id = self.request.form["id"]
            id = int(id)
        except Exception, e:
            msg = "ID Error: %s" % e
            self.page_msg(msg)
            return

        try:
            self.db.del_user(id)
        except Exception, e:
            msg = "Can't delete user wirth id '%s': %s" % (id, e)
        else:
            msg = "User with id '%s' deleted." % id

        self.page_msg(msg)

    def user_details(self):
        user_id = self.request.form['id']
        user_details = self.db.get_userdata_by_userid(
            user_id, select_items=["*"]
        )
        if debug:
            self.page_msg("User Data Details:", user_details)
        user_details = [
            {"key":k, "value":v} for k,v in user_details.iteritems()
        ]
        return user_details

    def _pass_reset_class(self):
        from PyLucid.modules.auth import pass_reset
        p = pass_reset.PassReset(self.request, self.response)
        return p

    def new_password_form(self, user_id=None):
        """
        Setzten eines neuen Passwortes für einen bestehenden User
        Wird im grunde von PyLucid.modules.auth gemacht.
        """
        if not user_id:
            user_id = self.request.form["id"]
        url = self.URLs.currentAction()

        # Die interne Seite "new_password_form" ist hier an diese Methode
        # verknüpft, damit im _install Bereich ein Zugriff auch möglich ist.
        self._pass_reset_class().new_password_form(url, user_id)

    def set_new_password(self):
        if debug:
            self.page_msg(self.request.form)

        try:
            user_id = int(self.request.form['user_id'])
        except (ValueError, KeyError):
            self.page_msg.red("Form Error!")
            return

        try:
            self._pass_reset_class().set_userpassword_by_userid(user_id)
        except Exception, e:
            self.page_msg.red("Can't save new password:", e)
        else:
            self.page_msg.green("New Password saved.")
