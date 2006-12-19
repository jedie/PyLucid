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
from PyLucid.system.tools import MD5Checker


class AuthData(object):
    md5username = None
    salt = None
    challenge = None

    def __init__(self, seed=None):
        self.seed = seed

    def _make_salt(self):
        seed = "%s%s" % (time.clock(), self.seed)
        salt = random.Random(seed).randint(10000,99999)
        return salt

    def make_new_salt(self):
        self.salt = self._make_salt()

    def make_new_challenge(self):
        self.challenge = self._make_challenge()


class LoginVerifier(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(LoginVerifier, self).__init__(*args, **kwargs)

        self.md5check = MD5Checker()

    def _error_msg(self, log_msg, public_msg):
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

    def check_md5_login(self):
        """
        Überprüfen der md5-JavaScript-Logindaten
        - Der Username wurde schon in "Step 1" eingegeben.
            - Die MD5 Summe des Usernamens steckt in einem Cookie
            - Der md5username wird nochmal überprüft
        """
        if debug:
            self.session.debug()

        if debug:
            self.page_msg("form data:", self.request.form)
        try:
            md5_a2  = self.request.form["md5_a2"]
            md5_b  = self.request.form["md5_b"]
        except KeyError, e:
            # Formulardaten nicht vollständig
            if debug:
                self.page_msg("CGI-Keys: ", self.request.form.keys())
            msg = self._error_msg(
                "Form data not complete! KeyError: '%s'" % e,
                "LogIn Error!"
            )
            raise PasswordError(msg)

        try:
            md5username = self.request.cookies["md5username"].value
            self.md5check(md5username) # Falls falsch -> ValueError
        except (KeyError, ValueError):
            msg = self._error_msg(
                "Can't get md5username from cookie!",
                "LogIn Error!"
            )
            raise PasswordError(msg)


#~ print "\n 4.1. aus der DB md5checksum: '%s'" % md5checksum

#~ print "\n 4.2. decrypt(md5checksum, key=md5_b):",
#~ md5checksum = decrypt(md5checksum, key=md5_b)
#~ print "'%s'" % md5checksum

#~ print "\n 4.3. md5(md5checksum + challenge):",
#~ md5check = md5(md5checksum + challenge)
#~ print "'%s'" % md5check

#~ print "\n 4.4. Vergleich: %s == %s" % (md5check, md5_a2)

        try:
            md5checksum = crypt.decrypt(md5_a2, md5_b)
        except crypt.CryptError, e:
            raise LogInError(e)

        challenge = self.session["challenge"]
        md5checksum = md5.new(md5checksum + challenge).hexdigest()


        self.page_msg("OK:", db_md5checksum, md5checksum)
        #~ return

        #~ try:
            #~ # Die Zufallszahl beim login, wird aus der Datenbank geholt, nicht
            #~ # aus den zurück geschickten Formular-Daten
            #~ rnd_login = self.session["rnd_login"]
        #~ except KeyError:
            #~ self._error(
                #~ "Error-0: Can't get rnd_login number from session",
                #~ "LogIn Error! (error:0)"
            #~ )
            #~ return

        #~ if (len( md5_a2 ) != 32) or (len( md5_b ) != 32):
            #~ self._error(
                #~ "Error-1: len( form_pass ) != 32",
                #~ "LogIn Error! (error:1)"
            #~ )
            #~ return

        #~ try:
            #~ # Daten zum User aus der DB holen
            #~ db_userdata = self.db.md5_login_userdata(username)
        #~ except KeyError:
            #~ # User exisiert nicht.
            #~ self.exist_one_user_test()
            #~ log_msg = "Error: User '%s' unknown %s" % (username,e)
            #~ public_msg = "User '%s' unknown!" % username
            #~ self._error(log_msg, public_msg)
        #~ except Exception, e:
            #~ # Unbekannter Fehler
            #~ self.exist_one_user_test()
            #~ log_msg = "Unknown error: Can't get Userdata: %s" % e
            #~ public_msg = "User '%s' unknown!" % username
            #~ self._error(log_msg, public_msg)


        #~ # Ersten MD5 Summen vergleichen
        #~ if md5_a2 != db_userdata["pass1"]:
            #~ self._error(
                #~ 'Error-2: md5_a2 != db_userdata["pass1"]',
                #~ "LogIn Error: Wrong Password! (error:2)"
            #~ )
            #~ return

        #~ try:
            #~ # Mit erster MD5 Summe den zweiten Teil des Passworts aus
            #~ # der DB entschlüsseln
            #~ db_pass2 = crypt.decrypt( db_userdata["pass2"], md5_a2 )
        #~ except Exception, e:
            #~ self._error(
                #~ "Error-3: decrypt db_pass2 failt: %s" % e ,
                #~ "LogIn Error: Wrong Password! (error:3)"
            #~ )
            #~ return

        #~ # An den entschlüßelten, zweiten Teil des Passwortes, die Zufallszahl
        #~ # dranhängen...
        #~ db_pass2 += str( rnd_login )
        #~ # ...daraus die zweite MD5 Summe bilden
        #~ db_pass2md5 = md5.new( db_pass2 ).hexdigest()

        #~ # Vergleichen der zweiten MD5 Summen
        #~ if db_pass2md5 != md5_b:
            #~ self._error(
                #~ 'Error-4: db_pass2md5 != md5_b |%s|' % db_pass2 ,
                #~ "LogIn Error: Wrong Password! (error:4)"
            #~ )
            #~ return



    #_________________________________________________________________________





#=============================================================================
#=============================================================================
#=============================================================================



class auth(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(auth, self).__init__(*args, **kwargs)

        self.staticTags = self.request.staticTags

        self.auth_data = AuthData(self.session["client_IP"])

    #_________________________________________________________________________

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
            if len(md5username) != 32:
                self.page_msg.red("URL error!")
            else:
                # Formular zum eingeben des Passwortes:
                self.password_input(md5username)
                return

        # Formular zum eingeben des Usernamens:
        context = {
            "username_input" : True,
            "url": self.URLs.actionLink("login"),
        }
        #~ self.page_msg(context)
        self.templates.write("login", context)

    def password_input(self, md5username, display_reset_link=False):
        """
        Login Step 2

        -Anhand des Usernamens (als MD5 Summe) wird der Passwort 'salt' Wert
        aus der DB geholt.
        -Der User kann nun das Passwort eingeben
        """
        #~ if debug:
            #~ self.page_msg("form data:", self.request.form)
        #~ if function_info != None:
            #~ # Das Formular wurde irgendwie falsch abgeschickt
            #~ self.page_msg("submit error!")

        try:
            salt = self.db.get_userdata_by_md5username(md5username, "salt")
            salt = salt["salt"]
        except (KeyError, IndexError):
            self.page_msg.red("Username unknown!")
            self.login()
            return

        # Der Username ist ok -> Als cookie "speichern"
        self.response.set_cookie("md5username", md5username)

        if salt<10000 or salt>99999:
            self.page_msg.red("Internal Error: Salt value out of range.")
            if debug:
                self.page_msg("salt value from db: '%s'" % salt)
            self.page_msg("You must reset your password!")
            self.pass_reset_form()
            return
        else:
            self.auth_data.salt = salt

        #~ self.auth_data.challenge = self._make_salt()
        self.auth_data.challenge = "12345"

        self.session.makeSession() # Eine Session eröffnen

        # Zufallszahl "merken"
        self.session["challenge"] = challenge

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
        verifier = LoginVerifier(self.request, self.response)
        try:
            verifier.check_md5_login()
        except PasswordError, e:
            self.password_input()
            return




        # Wenn wir schon die Userdaten aus der DB holen, können wir gleich
        # alle holen, die nötig sind, wenn der login auch klappt
        select_items = ["id", "name", "md5checksum", "admin"]
        userdata = self.db.get_userdata_by_md5username(
            md5username, select_items
        )

        db_md5checksum = userdata["md5checksum"]

        try:
            self.check_md5_login(db_md5checksum, md5_a2, md5_b)
        except LogInError, e:
            # Login war nicht erfolgreich
            self._error(
                "check_md5_login() Error: %s" % e.args,
                "LogIn Error!"
            )
            self.password_input(md5username, display_reset_link=True)
            #~ self.login() # Login Seite wieder anzeigen
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

        select_items=["email"]
        try:
            userdata = self.db.get_userdata_by_username(username, select_items)
        except Exception, e:
            msg = "User unknown!"
            if debug: msg += " (Debug: %s)" % e
            self.page_msg.red(msg)
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

        #~ self.db_cache.create_table()

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
            self.pass_reset_form()
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
            try:
                self.__set_new_password(reset_data["username"])
            except SetNewPassError, e:
                self.page_msg.red(e)
                return

            self.page_msg.green("Update password successful.")
            self.db_cache.delete_object(reset_key)
            self.login() # Loginformular anzeigen
            return

        # Formular für Passwort eingabe senden
        context = {
            "salt": self._make_salt(),
            "url": self.URLs.currentAction(reset_key),
        }
        self.page_msg(context)
        self.templates.write("new_pass_form", context)

    def __set_new_password(self, username):
        """
        Setzt das neue Passwort für den User
        Wird von pass_reset() aufgerufen, wenn reset_data ok ist.
        """
        try:
            md5pass = self.request.form["md5pass"]
            salt, md5pass = md5pass.split("_")
            salt = int(salt)
        except Exception, e:
            raise SetNewPassError("Form Error: %s" % e)

        if salt<10000 or salt>99999:
            raise SetNewPassError("Form Error! Salt out of range.")

        pass1 = self.request.form.get("pass1", "")
        pass2 = self.request.form.get("pass2", "")
        if pass1!="" or pass2!="":
            self.page_msg.red(
                "Security node: The Plain Text Password was send back!!!"
            )

        if len(md5pass)!=32:
            raise SetNewPassError("md5pass brocken?!?!")

        md5_a = md5pass[:16]
        md5_b = md5pass[16:]

        # Ersten Teil der MD5 mit dem zweiten Zeil verschlüsseln
        md5checksum = crypt.encrypt(md5_a, md5_b)

        data = {
            "name": username,
            "md5checksum": md5checksum,
            "salt": salt,
        }
        if debug:
            self.page_msg("new user data:", data)
        try:
            self.db.update_userdata_by_name(**data)
        except Exception, e:
            raise SetNewPassError("Error, update db data: %s" % e)

    #_________________________________________________________________________

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



    #_________________________________________________________________________

    def logout(self):
        self.session.delete_session()
        self.page_msg.green("You are logged out.")

        # Damit der Logout-Link zu einem Login-Link wird...
        self.staticTags.setup()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True



class AuthError(Exception):
    pass

class PasswordError(AuthError):
    pass

class SetNewPassError(AuthError):
    pass
