#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout

Last commit info:
----------------------------------
LastChangedDate: $LastChangedDate$
Revision.......: $Rev$
Author.........: $Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__ = "$Rev$"



# Standart Python Module
import os, sys, md5, datetime
#~ from Cookie import SimpleCookie

## Dynamisch geladene Module:
## import random -> auth.make_login_page()


from PyLucid.system import crypt


# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
# Gleichzeitig wird Modul-Manager Debug ein/aus geschaltet
#~ debug = True
debug = False
# WICHTIG:
# Ist debug eingeschaltet, wird keine Password-Reset Email verschickt,
# sondern direkt angezeigt!


from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.system.tools import ChecksumChecker

from PyLucid.modules.auth.exceptions import *
from PyLucid.modules.auth.login_verifier import LoginVerifier
from PyLucid.modules.auth.auth_data import AuthData






class auth(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(auth, self).__init__(*args, **kwargs)

        self.staticTags = self.request.staticTags
        self.checksum_checker = ChecksumChecker().check
        self.auth_data = AuthData(self.session["client_IP"])


    def login(self, function_info=None):
        """
        Login Step 1

        Er muß erstmal den Usernamen eingeben.
        """
        if debug:
            self.page_msg("form data:", self.request.form)
            self.page_msg("cookie data:", self.request.cookies)

        if function_info != None:
            # In der URL steckt evtl. der Username?
            md5username = function_info[0]
            try:
                self.checksum_checker(md5username)
            except ValueError, e:
                if debug:
                    self.page_msg.red("Checksum check error: %s" % e)
                else:
                    self.page_msg.red("URL Error.")
            else:
                # Formular zum eingeben des Passwortes:
                self.auth_data.md5username = md5username
                self.password_input()
                return

        # Formular zum eingeben des Usernamens:
        context = {
            "username_input" : True,
            "url": self.URLs.actionLink("login"),
        }
        #~ self.page_msg(context)
        self.templates.write("login", context)

    def password_input(self, display_reset_link=False):
        """
        Login Step 2

        -Anhand des Usernamens (als MD5 Summe) wird der Passwort 'salt' Wert
        aus der DB geholt.
        -Der User kann nun das Passwort eingeben
        """
        if debug:
            self.page_msg("form data:", self.request.form)
            self.page_msg(self.auth_data.md5username)

        try:
            salt = self.db.get_userdata_by_md5username(
                self.auth_data.md5username, "salt"
            )
            salt = salt["salt"]
        except (KeyError, IndexError):
            self.page_msg.red("Username unknown!")
            self.auth_data.reset()
            self.login()
            return

        # Der Username ist ok -> Als cookie "speichern"
        self.response.set_cookie("md5username", self.auth_data.md5username)

        if salt<10000 or salt>99999:
            self.page_msg.red("Internal Error: Salt value out of range.")
            if debug:
                self.page_msg("salt value from db: '%s'" % salt)
            self.page_msg("You must reset your password!")
            self.pass_reset_form()
            return
        else:
            self.auth_data.salt = salt

        self.auth_data.make_new_challenge()
        #~ self.auth_data.challenge = "12345"

        self.session.makeSession() # Eine Session eröffnen

        # Zufallszahl "merken"
        self.session["challenge"] = self.auth_data.challenge

        if debug == True:
            self.session.debug()

        context = {
            "salt"          : self.auth_data.salt,
            "challenge"     : self.auth_data.challenge,
            "default_action": self.URLs.currentAction("error"),
            "url"           : self.URLs.actionLink("check_login"),
        }
        if display_reset_link:
            context["reset_link"] = self.URLs.actionLink("pass_reset_form")

        if debug:
            self.page_msg("jinja context:", context)
        self.templates.write("login", context)

    def check_login(self):
        """
        Überprüft die Daten vom abgeschickten LogIn-Formular und logt den User
        ein.
        - Der Username wurde vorher schon eingebenen und verifiziert.

        """
        verifier = LoginVerifier(
            self.request, self.response, self.checksum_checker
        )
        try:
            userdata = verifier.check_md5_login()
        except PasswordError, e:
            msg = "LogInError!"
            if debug:
                msg += " (%s)" % e
            self.page_msg.red(msg)
            self.auth_data.md5username = md5username
            self.password_input(display_reset_link=True)
            raise "To be continue..."
            return
        else:
            if debug:
                self.page_msg("Login check OK")
                self.page_msg(userdata)

        db_md5checksum = userdata["md5checksum"]

        # Alles in Ordnung, User wird nun eingeloggt:

        # Sessiondaten festhalten
        self.session["user_id"]     = userdata["id"]
        self.session["user"]        = userdata["name"]
        #~ sefl.session["user_group"]
        self.session["last_action"] = "login"
        if userdata['admin'] == 1:
            self.session["isadmin"] = True
        else:
            self.session["isadmin"] = False

        self.log.write(
            "OK:Session erstellt. User:'%s' sID:'%s'" % (
                self.session["user"], self.session["session_id"]
            )
        )
        self.page_msg.green("You are logged in.")

        # Login/Logout-Link aktualisieren
        self.staticTags.setup_login_link()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True

    def exist_one_user_test(self):
        """
        Schaut nach ob überhaupt irgendein User existiert.
        """
        test = self.db.select(
            select_items    = ["id"],
            from_table      = "md5users",
            limit           = 1,
        )
        if test != []:
            return

        # Es existieren überhaupt keine User!
        log_msg = public_msg = (
            "There exist no User!"
            " Please add a User in the _install section first."
        )
        self._error(log_msg, public_msg)


    #_________________________________________________________________________

    def logout(self):
        self.session.delete_session()
        self.page_msg.green("You are logged out.")

        # Damit der Logout-Link zu einem Login-Link wird...
        self.staticTags.setup()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True

    #_________________________________________________________________________
    # Passwort reset

    def _get_pass_reset(self):
        """ Gibt instanzierte Klasse rück """
        from PyLucid.modules.auth.pass_reset import PassReset
        return PassReset(self.request, self.response)

    def pass_reset_form(self, function_info=""):
        """ Formular für Passwort reset. (Eingabe: Username + EMail) """
        pass_reset = self._get_pass_reset()
        pass_reset.pass_reset_form(function_info)

    def check_pass_reset(self):
        """ Abgeschickes "password reset" Formular überprüfen. """
        pass_reset = self._get_pass_reset()
        pass_reset.check_pass_reset()

    def pass_reset(self, function_info=""):
        """ Überprüft eine Passwort reset Anforderung """
        pass_reset = self._get_pass_reset()
        pass_reset.pass_reset(function_info)





