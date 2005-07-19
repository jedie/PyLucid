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

__version__ = "v0.0.2"

__history__ = """
v0.0.2
    - auth-Klasse nach PyLucid_modules.user_auth ausgelagert
v0.0.1
    - erste Version
"""


# Standart Python Module
import cgitb;cgitb.enable()
import os, sys, md5


# eigene Module
from PyLucid_system import crypt






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