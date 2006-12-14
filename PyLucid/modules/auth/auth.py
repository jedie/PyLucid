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
import os, sys, md5, time, random, datetime
from Cookie import SimpleCookie

## Dynamisch geladene Module:
## import random -> auth.make_login_page()


# eigene Module -> DoTo -> crypt irgendwie anders hinterlegen!
from PyLucid.system import crypt


# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
# Gleichzeitig wird Modul-Manager Debug ein/aus geschaltet
debug = True
#~ debug = False
# WICHTIG:
# Ist debug eingeschaltet, wird keine Password-Reset Email verschickt,
# sondern direkt angezeigt!


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
        rnd_login = self._make_salt()

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

        #~ self.page_msg(context)
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

    def pass_reset_form(self, function_info=""):
        """
        User möchte sein Passwort zurück setzten.
        """
        try:
            old_username = function_info[0]
        except IndexError:
            old_username = ""

        context = {
            "user"  : old_username,
            "url"   : self.URLs.actionLink("check_pass_reset"),
        }
        self.page_msg(context)
        self.templates.write("pass_reset_form", context)

    def check_pass_reset(self):
        """
        Abgeschickes "password reset" form überprüfen.
        Sind alle Daten korrekt, wird die reset mail verschickt.
        """
        # Form daten holen
        try:
            username    = self.request.form["user"]
            email       = self.request.form["email"]
            if username=="": raise KeyError("username")
            if email=="": raise KeyError("email")
        except KeyError, e:
            # Formulardaten nicht vollständig
            self.page_msg.red("Form data not complete! (KeyError: %s)" % e)
            if debug: self.page_msg("form data:", self.request.form)
            self.pass_reset_form([self.request.form.get("user","")])
            return

        try:
            userdata = self.db.userdata(username)
        except Exception, e:
            self.page_msg.red("User unknown!")
            if debug: self.page_msg(Exception, e)
            self.pass_reset_form([username])
            return

        if userdata["email"] != email:
            self.page_msg.red("Wrong email adress!")
            if debug: self.page_msg("userdata:", userdata)
            self.pass_reset_form([username])
            return

        ##____________________________________________________________________
        ## Username und Mail OK

        reset_data = self._reset_data()
        reset_data["username"] = username

        formatDateTime = self.preferences["core"]["formatDateTime"]
        formatDateTime = formatDateTime.encode("utf8") # FIXME
        request_time = datetime.datetime.now().strftime(formatDateTime)

        if debug: self.page_msg("reset_data:", reset_data)

        ##____________________________________________________________________
        ## reset request merken

        seed = "%s%s" % (time.clock(), reset_data["ip"])
        reset_key = md5.new(seed).hexdigest()

        expiry_time = 24 * 60 * 60
        try:
            self.db_cache.put_object(reset_key, expiry_time, reset_data)
        except Exception, e:
            #~ msg = e.args
            #~ Duplicate entry
            self.page_msg.red("Sorry, can't insert data in db: %s" % e)
            return

        ##____________________________________________________________________
        ## EMail verschicken

        now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=expiry_time)
        expiry_date = now + delta
        expiry_date = expiry_date.strftime(formatDateTime)

        reset_link = self.URLs.absolute_command_link(
            "auth", "pass_reset", reset_key, addSlash=False
        )
        #~ reset_data["request_time"] = request_time
        context = reset_data
        context.update({
            "base_url"      : self.URLs.absoluteLink(),
            "reset_link"    : reset_link,
            "expiry_date"   : expiry_date,
        })

        if debug:
            self.page_msg(context)
            #~ self.session.debug()
            #~ self.preferences.debug()
            self.response.write("<strong>Debug - The mail:</strong>")

            self.response.write("<pre>")
            self.templates.write("pass_reset_email", context)
            self.response.write("</pre><hr />")

        ##____________________________________________________________________
        ## Info Seite über die verschickte email anzeigen:

        context = {
            "submited"      : True,
            "expiry_time"  : "%sSec." % expiry_time,
            "expiry_date"   : expiry_date,
        }
        #~ self.page_msg(context)
        self.templates.write("pass_reset_form", context)

    def pass_reset(self, function_info=""):
        """
        Überprüft eine Passwort reset Anforderung
        Es ist der direkte Link aus der EMail, die bei check_pass_reset()
        versendet wurde.
        Ist der reset-Link ok, wird die HTML-Form zum setzten eines neues
        Passwortes angezeigt.

        macht folgendes:
            - Gibt ein Formular zur eingabe des neuen Passwortes aus
            - Nimmt das Ergebnis des Formulars entgegen
        """
        try:
            reset_key = function_info[0]
        except KeyError:
            self.page_msg.red("Wrong reset url!")
            return

        if debug: self.page_msg("reset-Key:", reset_key)

        try:
            reset_data = self.db_cache.get_object(reset_key)
        except Exception, e:
            #~ msg = e.args
            self.page_msg.red("Sorry, can't get reset data from db: %s" % e)
            return

        current_reset_data = self._reset_data()

        if debug:
            self.page_msg("reset data:", reset_data)
            self.page_msg("current_reset_data:", current_reset_data)
            self.page_msg("form data:", self.request.form)

        for key in ("user_agent", "ip", "domain"):
            if reset_data[key] != current_reset_data[key]:
                self.page_msg.red("reset data check failt!")
                return

        if 'md5pass' in self.request.form:
            # Formular wurde abgeschickt!
            self.__set_new_password(reset_data["username"])
        else:
            # Formular für Passwort eingabe senden
            context = {
                "salt": self._make_salt(),
                "url": self.URLs.currentAction(reset_key),
            }
            self.page_msg(context)
            self.templates.write("new_pass_form", context)

    def __set_new_password(self, username, salt):
        """
        Setzt das neue Passwort für den User
        Wird von pass_reset() aufgerufen, wenn reset_data ok ist.
        """
        md5pass = self.request.form["md5pass"]
        pass1 = self.request.form.get("pass1", "")
        pass2 = self.request.form.get("pass2", "")
        if pass1!="" or pass2!="":
            self.page_msg.red(
                "Security node: The Plain Text Password was send back!!!"
            )

        if len(md5pass)!=32:
            self.page_msg.red("md5pass brocken?!?!")
            return

        self.page_msg("ok:", md5pass)
        md5_a = md5pass[:16]
        md5_b = md5pass[16:]

        # Ersten Teil der MD5 mit dem zweiten Zeil verschlüsseln
        md5checksum = crypt.encrypt(md5_a, md5_b)

        raise "Der salt fehlt hier noch!!!"


    def _reset_data(self):
        """
        """
        reset_data = {
            "user_agent": self.request.environ.get('HTTP_USER_AGENT', \
                                                                    "unknown"),
            "ip"        : self.session["client_IP"],
            "domain"    : self.session["client_domain_name"],
        }
        return reset_data

    def _make_salt(self):
        seed = "%s%s" % (time.clock(), self.session["client_IP"])
        salt = random.Random(seed).randint(10000,99999)
        return salt

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

