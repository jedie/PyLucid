#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout


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


import time, datetime, md5


# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
#~ debug = True
debug = False



from PyLucid.system import crypt
from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.modules.auth.auth_data import AuthData

from PyLucid.modules.auth.exceptions import *


class PassReset(PyLucidBaseModule):
    """
    Das Password eines Users wieder neu setzten
    """

    def __init__(self, *args, **kwargs):
        super(PassReset, self).__init__(*args, **kwargs)

        self.auth_data = AuthData(self.session["client_IP"])


    def pass_reset_form(self, function_info=""):
        """
        User möchte sein Passwort zurück setzten:
        - Formular für Passwort reset. (Eingabe: Username + EMail)
        """
        try:
            old_username = function_info[0]
        except IndexError:
            old_username = ""

        context = {
            "user"  : old_username,
            "url"   : self.URLs.actionLink("check_pass_reset"),
        }
        #~ self.page_msg(context)
        self.templates.write("pass_reset_form", context)

    def check_pass_reset(self):
        """
        Abgeschickes "password reset" Formular überprüfen.
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
        request_time = now.strftime(formatDateTime)

        reset_link = self.URLs.absolute_command_link(
            "auth", "pass_reset", reset_key, addSlash=False
        )
        #~ reset_data["request_time"] = request_time
        context = reset_data
        context.update({
            "base_url"      : self.URLs.absoluteLink(),
            "reset_link"    : reset_link,
            "request_time"  : request_time,
            "expiry_date"   : expiry_date,
        })

        mail_text = self.templates.get_rendered_page(
            "pass_reset_email", context
        )

        if debug:
            self.page_msg(context)
            #~ self.session.debug()
            #~ self.preferences.debug()
            self.response.write("<strong>Debug - The mail:</strong>")
            self.response.write("<pre>")
            self.response.write(mail_text)
            self.response.write("</pre>(Mail not send in debug mode.)<hr />")
        else:
            from_address = "PyLucid_automailer@%s" % self.URLs["host"]
            from PyLucid.tools.text_emails import send_text_email
            try:
                send_text_email(
                    # FIXME: solle eine Adresse aus den preferences ein!
                    from_address=from_address,
                    to_address=email,
                    subject="PyLucid passwort reset request",
                    text= mail_text
                )
            except Exception, e:
                self.page_msg.red("Can't send reset mail:", e)
                return
            else:
                self.page_msg.green(
                    "Reset Mail sended. Please check your Mails ;)"
                )

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
            if len(function_info[0]) != 32:
                raise ValueError
            int(function_info[0], 16) # Ist eine Hex-Zahl?
        except (KeyError, ValueError):
            self.page_msg.red("Wrong reset url!")
            return
        else:
            reset_key = function_info[0]

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
            #~ self.login() # Loginformular anzeigen
            return
        else:
            self.new_password_form(self.URLs.currentAction(reset_key))

    def new_password_form(self, url, user_id=None):

        self.auth_data.make_new_salt()
        new_salt = self.auth_data.salt

        # Formular für Passwort eingabe senden
        context = {
            "salt": new_salt,
            "url": url,
            "user_id": user_id,
        }
        #~ self.page_msg(context)
        self.templates.write("new_pass_form", context)

    def set_userpassword_by_userid(self, user_id):
        """
        Externe Methode für userhandling
        """
        select_items=["name"]
        username = self.db.get_userdata_by_userid(user_id, select_items)
        username = username["name"]
        self.__set_new_password(username)


    def __set_new_password(self, username):
        """
        Setzt das neue Passwort für den User
        Wird von pass_reset() aufgerufen, wenn reset_data ok ist.
        """
        try:
            md5pass = self.request.form["md5pass"]
            salt, md5pass = md5pass.split("_")
            if len(salt) != 5 or len(md5pass) != 32:
                raise ValueError("Length incorrect")
            int(md5pass, 16) # Ist Hex-Zahl?
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
            raise SetNewPassError(
                "Error, update db data! %s - %s" % (e.__class__, e)
            )

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

