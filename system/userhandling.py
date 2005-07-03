#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Stores every Session Data in pseudoclasses

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
        - Username u. RealName
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


"""

__version__ = "v0.0.1"

__history__ = """
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()

import os, sys, md5
from Cookie import SimpleCookie

# eigene Module
from system import config, crypt


## Dynamisch geladene Module:
## import random -> auth.make_login_page()



class auth:
    def __init__( self, db_handler, log_class, CGIdata, session_class ):
        self.MyCookie = SimpleCookie()

        self.db         = db_handler
        self.log        = log_class
        self.log.set_typ("login")
        self.session    = session_class
        self.CGIdata    = CGIdata

    ####################################################
    # LogIn

    def make_login_page( self ):
        "Holt das LogIn-Formular aus der DB und stellt es zusammen"
        import random

        try:
            login_form = self.db.get_internal_page( "login_form" )["content"]
        except Exception, e:
            return "Can't get internal page! Did you executed 'install_PyLucid.py' first ??? (%s)" % e

        try:
            login_form = login_form % {
                    "md5"           : config.system.md5javascript,
                    "md5manager"    : config.system.md5manager,
                    "rnd"           : random.randint(10000,99999),
                    "url"           : config.system.real_self_url + "?command=check_login"#os.environ['SCRIPT_NAME']
                }
        except Exception, e:
            return "Error in login_form! Please check DB. (%s)" % e

        return login_form

    def check_login( self ):
        "Überprüft die Daten vom abgeschickten LogIn-Formular und logt den User ein"

        try:
            username    = self.CGIdata["user"]
            form_pass1  = self.CGIdata["md5pass1"]
            form_pass2  = self.CGIdata["md5pass2"]
            rnd         = self.CGIdata["rnd"]
            md5login    = self.CGIdata["use_md5login"]
        except KeyError:
            # Formulardaten nicht vollständig
            msg  = "<h1>Internal Error:</h1>"
            #~ msg += "<p>CGI-data-debug: '%s'</p>" % self.CGIdata
            msg += "<h3>Form data not complete!</h3>"
            msg += "Did you run 'install_PyLucid.py'? Check login form in SQL table 'pages_internal'."
            return msg

        if md5login != "1":
            return "Klartext passwort übermittlung noch nicht fertig!"

        return self.check_md5_login( username, form_pass1, form_pass2, rnd )

    def check_md5_login( self, username, form_pass1, form_pass2, rnd ):
        "Überprüft die md5-JavaScript-Logindaten"

        if (len( form_pass1 ) != 32) or (len( form_pass2 ) != 32):
            self.log( "Error-0: len( form_pass ) != 32" )
            return "<h1>LogIn Error!</h1>(errortype:0)"

        try:
            # Daten zum User aus der DB holen
            db_userdata = self.db.md5_login_userdata( username )
        except Exception, e:
            # User exisiert nicht.
            self.log("Error: User '%s' unknown %s" % (username,e) )
            return "User '%s' unknown!" % username

        # Ersten MD5 Summen vergleichen
        if form_pass1 != db_userdata["pass1"]:
            self.log( 'Error-1: form_pass1 != db_userdata["pass1"]' )
            return "<h1>LogIn Error: Wrong Password!</h1>(errortype:1)"

        try:
            # Mit erster MD5 Summe den zweiten Teil des Passworts aus
            # der DB entschlüsseln
            db_pass2 = crypt.decrypt( db_userdata["pass2"], form_pass1 )
        except Exception, e:
            self.log( "Error-2: decrypt db_pass2 failt: %s" % e )
            return "<h1>LogIn Error: Wrong Password!</h1>(errortype:2)"

        # An den entschlüsselten, zweiten Teil des Passwortes, die Zufallszahl dranhängen...
        db_pass2 += rnd
        # ...daraus die zweite MD5 Summe bilden
        db_pass2md5 = md5.new( db_pass2 ).hexdigest()

        # Vergleichen der zweiten MD5 Summen
        if db_pass2md5 != form_pass2:
            self.log( 'Error-3: db_pass2md5 != form_pass2 |%s|' % db_pass2)
            return "<h1>LogIn Error: Wrong Password!</h1>(errortype:3)"

        # Alles in Ordnung, User wird nun eingeloggt:

        self.session.makeSession() # Eine Session eröffnen

        # Sessiondaten festhalten
        self.session["user_id"] = db_userdata["id"]
        self.session["user"]    = username
        self.session["isadmin"] = db_userdata['admin']
        self.session.update_session()

        self.log.write( "OK:Session erstellt. User:'%s' sID:'%s'" % (username, self.session.ID) )
        return "<h1>LogIn erfolgreich!</h1>"

    def logout( self ):
        self.session.delete_session()
        return "<h1>LogOut</h1>"



class usermanager:
    """
    Verwaltung von Userdaten in der DB


    Auth.Verfahren - User erstellen:
    ================================
    1. Client:
        1.1. User füllt Formular mit Name und Passwort aus.
        1.2. per JS: bilden aus ersten vier Zeichen eine MD5 Summe
        1.3. MD5 Summe + rechlichen Zeichen des Passworts zum Server schicken
    2. Server:
        2.1. restliche Zeichen des Passworts mit geschickter MD5 Summe verschlüsseln
        2.2. verschlüßeltes Passwort und sonstige Userdaten in DB eintragen


    Auth.Verfahren - Client Login:
    ==============================
    1. Client: schickt login-Anfrage
    2. Server:
        2.1. setzt SessionID per Cookie
        2.2. generiert Random-Zahl
        2.3. speichert Random-Zahl mit SessionID in DB
        2.4. schickt LogIn-Form mit Random-Zahl zum Client
    3. Client:
        3.1. eingetipptes Passwort wird aufgeteilt ersten vier Zeichen | rechtlichen zeichen
        3.2. erstellung der MD5 Summen:
            - MD5( ersten vier Zeichen )
            - MD5( rechlichen Zeichen + die Random-Zahl vom Server )
        3.3. senden des Usernamens (Klartext) + beide MD5-Summen
    4. Server:
        4.1. mit der ersten MD5 Summe wird das Passwort aus der DB entschlüsselt
        4.2. Random-Zahl per SessionID aus der DB holen
        4.3. mit dem entschlüsselten Klartext-Passwort und der Random-Zahl wird eine MD5 Summe gebildet
        4.4. vergleichen der zweiten MD5 summe vom Client und der gebilteten
    """
    def __init__( self, db_handler ):
        self.db = db_handler

    def add_user( self, Username, email, password, realname=None, admin=0):
        "legt einen neuen User in der DB an"

        if len(password)<8:
            raise "Password is too short (min 8 characters)!!!"

        normal_md5_pass = md5.new( password ).hexdigest()

        print "Add user in lucidCMS's normal user-table:",

        try:
            self.db.add_User( Username, realname, email, normal_md5_pass, admin )
            print "OK\n"
        except Exception, e:
            print "Can't insert! (%s)\n" % e

        pass1, pass2 = self.create_md5_pass( password )

        print "Add user in PyLucid's JS-md5 user-table:",
        try:
            self.db.add_md5_User( Username, realname, email, pass1, pass2, admin )
            print "OK\n"
        except Exception, e:
            print "Can't insert! (%s)\n" % e

    def create_md5_pass( self, password ):
        "Erstellt das JS-MD5 Passwort-Paar"

        # Teilt Passwort auf
        pass1 = password[:4]
        pass2 = password[4:]

        # Berechnet MD5 Summe aus dem ersten Teil des Passwortes
        pass1 = md5.new( pass1 ).hexdigest()

        # Verschlüsselt zweiten Teil der Passwortes mit der MD5 des ersten Teiles
        pass2 = crypt.encrypt( pass2, pass1 )

        return pass1, pass2


#~ usermanager("").create_password( "dasisteintest" )