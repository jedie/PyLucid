#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout
"""

__version__ = "0.2"

__history__ = """
v0.2
    - Security-Fix: Die Zufallszahl zur MD5 Bildung, wird nun in den Sessiondaten in der Datenbank
        zwischengespeichert und nicht mehr aus den zurück geschickten Formulardaten genommen. Somit
        wird abgesichert, das die Login-Anfrage von einem gleichen Client kommt.
v0.1.2
    - Verbesserungen:
        - Für Rückmeldungen wird nun page_msg benutzt
        - Nach einem Fehlgeschlagenen Login, wird das login Form mit dem alten Usernamen angezeigt
v0.1.1
    - logout benötigt auch "direct_out": True, damit der Cookie auch gelöscht wird ;)
v0.1.0
    - Anpassung an neuen Module-Manager
v0.0.2
    - time.sleep() bei falschem Login
    - Fehleranzeige beim Login mit Variable "Debug" veränderbar
v0.0.1
    - Umgebaut für den Module-Manager
    - aus der Klasse PyLucid_system.userhandling rausgenommen
"""



# Standart Python Module
import os, sys, md5, time
from Cookie import SimpleCookie

## Dynamisch geladene Module:
## import random -> auth.make_login_page()


# eigene Module
from PyLucid_system import crypt


# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
# Gleichzeitig wird Modul-Manager Debug ein/aus geschaltet
#~ Debug = True
Debug = False



class auth:

    module_manager_data = {
        "debug" : False,

        "login" : {
            "must_login"    : False,
            "direct_out"    : True,
        },
        "logout" : {
            "must_login"    : False,
            "must_admin"    : False,
            "direct_out"    : True,
        },
        "check_login" : {
            "must_login"    : False,
            "direct_out"    : True,
        },
    }

    def __init__( self, PyLucid ):
        self.MyCookie = SimpleCookie()

        self.config     = PyLucid["config"]
        #~ self.config.debug()
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.log        = PyLucid["log"]
        self.session    = PyLucid["session"]
        #~ self.session.debug()
        self.db         = PyLucid["db"]
        self.page_msg   = PyLucid["page_msg"]

    ####################################################
    # LogIn

    def login( self ):
        """
        Der User will einloggen.
        Holt das LogIn-Formular aus der DB und stellt es zusammen
        """
        import random
        rnd_login = random.randint(10000,99999)

        url = "%s?page_id=%s&amp;command=auth&amp;action=check_login" % (
            self.config.system.real_self_url, self.CGIdata["page_id"]
        )

        try:
            # Alten Usernamen, nach einem Fehlgeschlagenen Login, wieder anzeigen
            username = self.CGIdata["user"]
        except KeyError:
            username = ""

        self.session.makeSession() # Eine Session eröffnen
        # Zufallszahl "merken"
        self.session["rnd_login"] = rnd_login

        if Debug == True:
            self.session.debug()

        return self.db.get_internal_page(
            internal_page_name = "login",
            page_dict = {
                "user"          : username,
                "rnd"           : rnd_login,
                "url"           : url
            }
        )

    def check_login( self ):
        """
        Überprüft die Daten vom abgeschickten LogIn-Formular und logt den User ein
        """
        try:
            username    = self.CGIdata["user"]
            form_pass1  = self.CGIdata["md5pass1"]
            form_pass2  = self.CGIdata["md5pass2"]
        except KeyError, e:
            # Formulardaten nicht vollständig
            msg  = "<h1>Login Error:</h1>"
            msg += "<h3>Form data not complete: '%s'</h3>" %e
            msg += "<p>Have you enabled JavaScript?</p>"
            msg += "<p>Did you run 'install_PyLucid.py'? Check login form in SQL table 'pages_internal'.</p>"
            if Debug: msg += "CGI-Keys: " + str(self.CGIdata.keys())
            return msg

        return self.check_md5_login( username, form_pass1, form_pass2 )

    def _error( self, log_msg, public_msg ):
        """Fehler werden abhängig vom Debug-Status angezeigt/gespeichert"""
        self.log( log_msg )
        self.session.delete_session()
        #~ time.sleep(3)
        self.page_msg( public_msg )
        if Debug:
            # Debug Modus: Es wird mehr Informationen an den Client geschickt
            self.page_msg( "Debug:",log_msg )
        # Login-Form wieder anzeigen
        return self.login()

    def check_md5_login( self, username, form_pass1, form_pass2 ):
        """
        Überprüft die md5-JavaScript-Logindaten
        """
        try:
            # Die Zufallszahl beim login, wird aus der Datenbank geholt, nicht aus
            # den zurück geschickten Formular-Daten
            rnd_login = self.session["rnd_login"]
        except KeyError:
            return self._error(
                "Error-0: Can't get rnd_login number from session",
                "LogIn Error! (error:0)"
            )

        if (len( form_pass1 ) != 32) or (len( form_pass2 ) != 32):
            return self._error(
                "Error-1: len( form_pass ) != 32",
                "LogIn Error! (error:1)"
            )

        try:
            # Daten zum User aus der DB holen
            db_userdata = self.db.md5_login_userdata( username )
        except Exception, e:
            # User exisiert nicht.
            return self._error(
                "Error: User '%s' unknown %s" % (username,e) ,
                "User '%s' unknown!" % username
            )

        # Ersten MD5 Summen vergleichen
        if form_pass1 != db_userdata["pass1"]:
            return self._error(
                'Error-2: form_pass1 != db_userdata["pass1"]',
                "LogIn Error: Wrong Password! (error:2)"
            )

        try:
            # Mit erster MD5 Summe den zweiten Teil des Passworts aus
            # der DB entschlüsseln
            db_pass2 = crypt.decrypt( db_userdata["pass2"], form_pass1 )
        except Exception, e:
            return self._error(
                "Error-3: decrypt db_pass2 failt: %s" % e ,
                "LogIn Error: Wrong Password! (error:3)"
            )

        # An den entschlüßelten, zweiten Teil des Passwortes, die Zufallszahl dranhängen...
        db_pass2 += str( rnd_login )
        # ...daraus die zweite MD5 Summe bilden
        db_pass2md5 = md5.new( db_pass2 ).hexdigest()

        # Vergleichen der zweiten MD5 Summen
        if db_pass2md5 != form_pass2:
            return self._error(
                'Error-4: db_pass2md5 != form_pass2 |%s|' % db_pass2 ,
                "LogIn Error: Wrong Password! (error:4)"
            )

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
        self.session.update_session()

        self.log.write( "OK:Session erstellt. User:'%s' sID:'%s'" % (username, self.session.ID) )
        self.page_msg( "You are logged in." )

    def logout( self ):
        self.session.delete_session()
        self.page_msg( "You are logged out." )



