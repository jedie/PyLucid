#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Benutzerverwalung für secure-MD5-JavaScript login

wird erstmal nur von install_PyLucid.py verwendet!

Anmerkung zur User-Verwaltung von lucidCMS
==========================================

    -= Die SQL-Tabellen zur Userverwaltung =-

"lucid_users" bzw. "lucid_md5users"
-----------------------------------
    Hier werden die forhandenen User gespeichert.

    "lucid_users" ist die original Tabelle von ludidCMS
    "lucid_md5users" ist die JS-md5-Tabellenversion von PyLucid

    Bisher gibt es keinen sync-Modus zwischen den beiden Tabellen!!!
    Mit "install_PyLucid.py" - "add-Admin" werden in beiden Tabellen
    die User angelegt.

    Informationen gespeichert werden:
        - Username u. realname
        - email-Adresse
        - Passwort
        - Admin =1 o. =0

    Admin sagt nur darüber aus, ob er alle Rechte hat (=1) oder ein
    normaler User (=0) ist.

"lucid_user_group"-Tabelle
--------------------------
    Hierdrin wird festgehalten, welcher Gruppe ein User angehört
    Das ganze funktioniert nur über die IDs.

"lucid_groups"-Tabelle
----------------------
    Speichert die User-Gruppen.

    gepsicherte Infos:
        - Gruppen-ID
        - pluginID
        - Gruppenname
        - Sektion
        - Beschreibung




Auth.Verfahren - User erstellen:
================================
1. Client:
    1.1. User füllt Formular mit Name und Passwort aus.
    1.2. per JS: bilden aus ersten vier Zeichen eine MD5 Summe
    1.3. MD5 Summe + rechlichen Zeichen des Passworts zum Server schicken
2. Server:
    2.1. restliche Zeichen des Passworts mit geschickter MD5 Summe verschlüsseln
    2.2. verschlüßeltes Passwort und sonstige Userdaten in DB eintragen

Ist noch nicht implementiert!


Auth.Verfahren - Client Login:
==============================
1. Client: schickt login-Anfrage
2. Server:
    2.1. setzt SessionID per Cookie
    2.2. generiert Random-Zahl
    2.3. speichert Random-Zahl mit SessionID in DB
    2.4. schickt LogIn-Form mit Random-Zahl zum Client
3. Client:
    3.1. eingetipptes Passwort wird aufgeteilt ersten vier
        Zeichen | rechtlichen zeichen
    3.2. erstellung der MD5 Summen:
        - MD5( ersten vier Zeichen )
        - MD5( rechlichen Zeichen + die Random-Zahl vom Server )
    3.3. senden des Usernamens (Klartext) + beide MD5-Summen
4. Server:
    4.1. mit der ersten MD5 Summe wird das Passwort aus der DB entschlüsselt
    4.2. Random-Zahl per SessionID aus der DB holen
    4.3. mit dem entschlüsselten Klartext-Passwort und der Random-Zahl wird
        eine MD5 Summe gebildet
    4.4. vergleichen der zweiten MD5 summe vom Client und der gebilteten
"""

__version__ = "0.2"

__history__ = """
v0.2
    - Anderes Handling wenn self.runlevel.is_install()
v0.1
    - Anpassung an PyLucid v0.7
v0.0.2
    - auth-Klasse nach PyLucid_modules.user_auth ausgelagert
v0.0.1
    - erste Version
"""

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
        if "add user" in self.request.form:
            # Es wurde das Formular abgeschickt
            self.add_user_action()
        elif "save" in self.request.form:
            self.save_changes()
        elif "delete" in self.request.form:
            self.delete_user()

        self.user_table()

        context = {"url": self.URLs.currentAction()}

        # Bei _install soll i.d.R. ein admin erstellt werden, deswegen soll
        # der Admin-Button "checked" sein
        if self.runlevel.is_install():
            context["runlevel_is_install"] = True
        else:
            context["runlevel_is_install"] = False

        #~ self.page_msg(context)
        self.templates.write("add_user", context)

    def user_table(self):
        user_list = self.db.user_data_list()
        context = {
            "url" : self.URLs.currentAction(),
            "user_list": user_list,
        }
        self.templates.write("user_table", context)

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
            pass1 = self.request.form["pass1"]
            pass2 = self.request.form["pass2"]
        except KeyError, e:
            msg = (
                "Formular Error: Key '%s' not found!\n"
                "No User added."
            ) % e
            self.page_msg(msg)
            return

        if pass1!=pass2:
            msg = (
                "Password 1 and password 2 are not the same!\n"
                "No User added!"
            )
            self.page_msg(msg)
            return

        if len(pass1)<8:
            msg = (
                "Password is too short (min 8 characters)!\n"
                "No User added!"
            )
            self.page_msg(msg)
            return

        realname = self.request.form.get("realname","")
        is_admin = self.request.form.get("is_admin", False)

        # Das Klartext-Password verschlüsseln
        pass1, pass2 = self.create_md5_pass(pass1)

        try:
            self.db.add_md5_User(
                username, realname, email, pass1, pass2, is_admin
            )
        except Exception, e:
            self.page_msg("Can't insert user! (%s)\n" % e)
        else:
            self.page_msg("User '%s' added." % username)


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


    def create_md5_pass( self, password ):
        """Erstellt das JS-MD5 Passwort-Paar"""

        # Teilt Passwort auf
        pass1 = ""
        pass2 = ""
        switcher = False
        for current_char in password:
            if switcher == False:
                pass1 += current_char
                switcher = True
            else:
                pass2 += current_char
                switcher = False

        # Berechnet MD5 Summe aus dem ersten Teil des Passwortes
        pass1 = md5.new( pass1 ).hexdigest()

        # Verschlüsselt zweiten Teil der Passwortes mit der MD5 des ersten Teiles
        pass2 = crypt.encrypt( pass2, pass1 )

        return pass1, pass2

    def pass_recovery(self, old_user="", old_email=""):
        print self.db.get_internal_page("pass_recovery")["content"] % {
            "url"   : self.action_url + "send_email",
            "user"  : cgi.escape(old_user),
            "email" : cgi.escape(old_email),
        }

    def send_email( self ):
        try:
            username    = self.CGIdata["user"]
            email_adr   = self.CGIdata["email"]
        except KeyError, e:
            self.page_msg( "Form error. No Key %s" % e )
            # Eingabe wieder anzeigen
            self.pass_recovery()
            return

        try:
            userdata = self.db.userdata( username )
        except Exception, e:
            self.page_msg( "Unknown user." )
            self.page_msg( e )
            # Eingabe wieder anzeigen
            self.pass_recovery( username, email_adr )
            return

        if userdata["email"] != email_adr:
            self.page_msg( "Wrong email Adress." )
            # Eingabe wieder anzeigen
            self.pass_recovery( username, email_adr )
            return

        # Username und email stimmen überein. Also wird eine Mail
        # geschickt.

        self.CGIdata.debug()

        email_text = self.db.get_internal_page("pass_recovery_email1")

        #~ email_text = email_text % {
            #~ "cms_name" : "test",
            #~ "from_info" :
            #~ "recovery_link"
        #~ }

        #~ self.tools.email().send(
            #~ to      = email_adr,
            #~ subject = "Request Password recovery.",
            #~ text    = "Your Password"
        #~ )

        print "OK"
        return



#~ usermanager("").create_password( "dasisteintest" )


