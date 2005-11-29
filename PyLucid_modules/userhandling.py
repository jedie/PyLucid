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


"""

__version__ = "0.0.2"

__history__ = """
v0.0.2
    - auth-Klasse nach PyLucid_modules.user_auth ausgelagert
v0.0.1
    - erste Version
"""


# Standart Python Module
import cgitb;cgitb.enable()
import os, sys, cgi, md5


# eigene Module
from PyLucid_system import crypt






class userhandling:
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

    module_manager_data = {
        "debug" : False,
        #~ "debug" : True,

        "manage_user": {
            "must_login"    : True,
            "must_admin"    : True,
            "CGI_dependent_actions": {
                "save_changes": {
                    "CGI_laws"      : {"save": "save"}, # Wert vom angeklicken Button
                    "get_CGI_data"  : {"id": int, "name": str, "email": str, "realname": str, "admin": int}
                },
                "add_user": {
                    "CGI_laws"      : {"add user": "add user"}, # Wert vom angeklicken Button
                    "get_CGI_data"  : {"username": str, "email": str, "realname": str, "admin": int}
                },
                "del_user": {
                    "CGI_laws"      : {"del": "del"}, # Wert vom angeklicken Button
                    "get_CGI_data"  : {"id": int}
                },
            }
        },
        "add_user" : {
            "must_login"    : True,
            "must_admin"    : True,
        },
        "pass_recovery" : {
            "must_login"    : False,
            "must_admin"    : False,
        },
        "send_email" : {
            "must_login"    : False,
            "must_admin"    : False,
        },
    }

    def __init__( self, PyLucid ):
        self.db         = PyLucid["db"]
        self.CGIdata    = PyLucid["CGIdata"]
        self.page_msg   = PyLucid["page_msg"]
        self.tools      = PyLucid["tools"]
        self.URLs       = PyLucid["URLs"]

    def manage_user(self):
        """ Verwaltung von Usern """

        # Eingabemaske für einen neuen user
        add_user_form = self.db.get_internal_page(
            internal_page_name = "add_user_form",
            page_dict = {
                "url": self.URLs["main_action"],
            }
        )["content"]

        # Interne Seite anzeigen
        self.db.print_internal_page(
            internal_page_name = "manage_user",
            page_dict = {
                "user_table"    : self.get_user_table(),
                "add_user_form" : add_user_form,
            }
        )

    def get_user_table(self):
        table  = "<table>\n"
        table += "<tr>\n"
        table += "<th>name</th>\n"
        table += "<th>realname</th>\n"
        table += "<th>email</th>\n"
        table += "<th>admin</th>\n"
        table += "</tr>\n"
        table_data = self.db.user_table_data()
        user_count = len(table_data)
        for user in table_data:
            table += "<tr>\n"

            table += '\t<form method="post" action="%s">\n' % self.URLs["main_action"]
            table += '\t<input name="id" type="hidden" value="%s" />\n' % user["id"]
            table += '\t<td><input name="name" type="text" value="%s" size="15" maxlength="50" /></td>\n' % user["name"]
            table += '\t<td><input name="realname" type="text" value="%s" size="20" maxlength="50" /></td>\n' % user["realname"]
            table += '\t<td><input name="email" type="text" value="%s" size="30" maxlength="50" /></td>\n' % user["email"]

            if user["admin"]==1:
                checked = ' checked="checked"'
            else:
                checked = ""
            table += '\t<td><input type="checkbox" name="admin" value="1"%s /></td>\n' % checked

            table += '\t<td><input type="submit" value="save" name="save" /></td>\n'
            if user_count > 1:
                # Den letzten User kann man nicht löschen ;)
                table += '\t<td><input type="submit" value="del" name="del" /></td>\n'
            table += "\t</form>\n"
            table += "</tr>\n"

        table += "</table>\n"
        return table


    def save_changes(self, id, name, email, realname="", admin=0):
        try:
            self.db.update_userdata(id, user_data={"name": name, "realname": realname, "email": email, "admin": admin})
        except Exception, e:
            self.page_msg("Error saving user data (id: %s): %s" % (id, e))
        else:
            self.page_msg( "User data saved!" )

        self.manage_user() # "Menü" wieder anzeigen


    def add_user(self, username, email, realname="", admin=0):
        """legt einen neuen User in der DB an"""
        try:
            # Falls das Passwort nur aus Zahlen besteht, wurde es in CGIdata
            # in eine echte Zahl umgewandelt, was hier aber nicht erwünscht war!
            pass1 = str(self.CGIdata["pass1"])
            pass2 = str(self.CGIdata["pass2"])
        except Exception,e:
            self.page_msg("Can't get password! No data where added!")
            return

        if pass1!=pass2:
            self.page_msg("Password verification failt! No data where added!")
            return

        if len(pass1)<8:
            self.page_msg("Password is too short (min 8 characters)! No data where added!")
            return

        # Das Klartext-Password verschlüsseln
        pass1, pass2 = self.create_md5_pass(pass1)

        try:
            self.db.add_md5_User( username, realname, email, pass1, pass2, admin )
        except Exception, e:
            self.page_msg("Can't insert! (%s)\n" % e)
        else:
            self.page_msg("User '%s' add." % username)

        if self.CGIdata.has_key("install_PyLucid"):
            # wurde aus install_PyLucid aufgerufen, dann gibt es kein Menü!
            return

        self.manage_user() # "Menü" wieder anzeigen


    def del_user(self, id):
        try:
            self.db.del_user(id)
        except Exception, e:
            self.page_msg( "Can't delete user wirth id '%s': %s" % (id, e) )
        else:
            self.page_msg( "User with id '%s' deleted." % id )

        self.manage_user() # "Menü" wieder anzeigen


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


