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
import os, sys, md5, time, random
from Cookie import SimpleCookie

## Dynamisch geladene Module:
## import random -> auth.make_login_page()


# eigene Module -> DoTo -> crypt irgendwie anders hinterlegen!
from PyLucid.system import crypt


# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
# Gleichzeitig wird Modul-Manager Debug ein/aus geschaltet
#~ debug = True
debug = False


from PyLucid.system.BaseModule import PyLucidBaseModule

class auth(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(auth, self).__init__(*args, **kwargs)

        self.staticTags = self.request.staticTags

    #_________________________________________________________________________

    def login(self, display_reset_link=False):
        """
        Der User will einloggen.
        Holt das LogIn-Formular aus der DB und stellt es zusammen
        """
        rnd_login = random.randint(10000,99999)

        url = self.URLs.actionLink("check_login")

        # Alten Usernamen, nach einem Fehlgeschlagenen Login, wieder anzeigen
        username = self.request.form.get("user", "")

        self.session.makeSession() # Eine Session eröffnen

        # Zufallszahl "merken"
        self.session["rnd_login"] = rnd_login

        if debug == True:
            self.session.debug()

        context = {
            "user"          : username,
            "rnd"           : rnd_login,
            "url"           : url,
        }
        if display_reset_link:
            context["reset_link"] = self.URLs.actionLink("pass_reset_form")

        self.page_msg(context)
        self.templates.write("login", context)

    def check_login(self):
        """
        Überprüft die Daten vom abgeschickten LogIn-Formular und logt den User
        ein
        """
        try:
            username    = self.request.form["user"]
            form_pass1  = self.request.form["md5pass1"]
            form_pass2  = self.request.form["md5pass2"]
        except KeyError, e:
            # Formulardaten nicht vollständig
            self.page_msg.red("Form data not complete! KeyError: '%s'" % e)
            if debug:
                self.page_msg("CGI-Keys: ", self.request.form.keys())
            self.login() # Login Seite wieder anzeigen
            return

        try:
            self.check_md5_login(username, form_pass1, form_pass2)
        except LogInError, e:
            self.page_msg.red(*e.args)
            self.login(display_reset_link=True) # Login Seite wieder anzeigen


    def _error(self, log_msg, public_msg):
        """Fehler werden abhängig vom Debug-Status angezeigt/gespeichert"""
        self.log(log_msg)

        self.session["isadmin"] = False
        self.session["user"] = False
        # Soll beim commit aktualisiert werden:
        self.session.state = "update session"

        if self.preferences["ModuleManager_error_handling"] == False:
            msg = "%s - Debug: %s" % (public_msg, log_msg)
        else:
            msg = public_msg

        raise LogInError(msg)

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

    def check_md5_login(self, username, form_pass1, form_pass2):
        """
        Überprüft die md5-JavaScript-Logindaten
        """
        if debug:
            self.session.debug()
        try:
            # Die Zufallszahl beim login, wird aus der Datenbank geholt, nicht
            # aus den zurück geschickten Formular-Daten
            rnd_login = self.session["rnd_login"]
        except KeyError:
            self._error(
                "Error-0: Can't get rnd_login number from session",
                "LogIn Error! (error:0)"
            )
            return

        if (len( form_pass1 ) != 32) or (len( form_pass2 ) != 32):
            self._error(
                "Error-1: len( form_pass ) != 32",
                "LogIn Error! (error:1)"
            )
            return

        try:
            # Daten zum User aus der DB holen
            db_userdata = self.db.md5_login_userdata(username)
        except KeyError:
            # User exisiert nicht.
            self.exist_one_user_test()
            log_msg = "Error: User '%s' unknown %s" % (username,e)
            public_msg = "User '%s' unknown!" % username
            self._error(log_msg, public_msg)
        except Exception, e:
            # Unbekannter Fehler
            self.exist_one_user_test()
            log_msg = "Unknown error: Can't get Userdata: %s" % e
            public_msg = "User '%s' unknown!" % username
            self._error(log_msg, public_msg)


        # Ersten MD5 Summen vergleichen
        if form_pass1 != db_userdata["pass1"]:
            self._error(
                'Error-2: form_pass1 != db_userdata["pass1"]',
                "LogIn Error: Wrong Password! (error:2)"
            )
            return

        try:
            # Mit erster MD5 Summe den zweiten Teil des Passworts aus
            # der DB entschlüsseln
            db_pass2 = crypt.decrypt( db_userdata["pass2"], form_pass1 )
        except Exception, e:
            self._error(
                "Error-3: decrypt db_pass2 failt: %s" % e ,
                "LogIn Error: Wrong Password! (error:3)"
            )
            return

        # An den entschlüßelten, zweiten Teil des Passwortes, die Zufallszahl
        # dranhängen...
        db_pass2 += str( rnd_login )
        # ...daraus die zweite MD5 Summe bilden
        db_pass2md5 = md5.new( db_pass2 ).hexdigest()

        # Vergleichen der zweiten MD5 Summen
        if db_pass2md5 != form_pass2:
            self._error(
                'Error-4: db_pass2md5 != form_pass2 |%s|' % db_pass2 ,
                "LogIn Error: Wrong Password! (error:4)"
            )
            return

        # Alles in Ordnung, User wird nun eingeloggt:

        # Sessiondaten festhalten
        del self.session["rnd_login"] # Brauchen wir nicht mehr
        self.session["user_id"]     = db_userdata["id"]
        self.session["user"]        = username
        #~ sefl.session["user_group"]
        self.session["last_action"] = "login"
        if db_userdata['admin'] == 1:
            self.session["isadmin"] = True
        else:
            self.session["isadmin"] = False

        self.log.write(
            "OK:Session erstellt. User:'%s' sID:'%s'" % (
                username, self.session["session_id"]
            )
        )
        self.page_msg.green("You are logged in.")

        # Login/Logout-Link aktualisieren
        self.staticTags.setup_login_link()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True

    #_________________________________________________________________________

    def pass_reset_form(self):
        raise To be continued...

    #_________________________________________________________________________

    def logout(self):
        self.session.delete_session()
        self.page_msg.green("You are logged out.")

        # Damit der Logout-Link zu einem Login-Link wird...
        self.staticTags.setup()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True



class LogInError(Exception):
    pass

