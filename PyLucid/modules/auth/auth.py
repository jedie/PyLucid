#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout
"""

__version__ = "0.2.2"

__history__ = """
v0.2.2
    - Nutzt raise-Fehlerseite
v0.2.1
    - Login-Fehler-Bug behoben
v0.2
    - Security-Fix: Die Zufallszahl zur MD5 Bildung, wird nun in den
        Sessiondaten in der Datenbank zwischengespeichert und nicht mehr aus
        den zurück geschickten Formulardaten genommen. Somit wird abgesichert,
        das die Login-Anfrage von einem gleichen Client kommt.
v0.1.2
    - Verbesserungen:
        - Für Rückmeldungen wird nun page_msg benutzt
        - Nach einem Fehlgeschlagenen Login, wird das login Form mit dem alten
            Usernamen angezeigt
v0.1.1
    - logout benötigt auch "direct_out": True, damit der Cookie auch gelöscht
        wird ;)
v0.1.0
    - Anpassung an neuen Module-Manager
v0.0.2
    - time.sleep() bei falschem Login
    - Fehleranzeige beim Login mit Variable "Debug" veränderbar
v0.0.1
    - Umgebaut für den Module-Manager
    - aus der Klasse PyLucid_system.userhandling rausgenommen
"""

__todo__ = """
    -Bug: Direkt nach logout kann man sich nicht neu einloggen (erst beim
        nächsten Request geht's wieder)
    -Bann-Liste: Nach drei falschen Loginversuchen, sollte die IP für eine
        gewisse Zeit gesperrt werden!!!
"""



# Standart Python Module
import os, sys, md5, time
from Cookie import SimpleCookie

## Dynamisch geladene Module:
## import random -> auth.make_login_page()


# eigene Module -> DoTo -> crypt irgendwie anders hinterlegen!
from PyLucid.system import crypt

from PyLucid.system.exceptions import LogInError


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

    def login(self):
        """
        Der User will einloggen.
        Holt das LogIn-Formular aus der DB und stellt es zusammen
        """
        import random
        rnd_login = random.randint(10000,99999)

        url = self.URLs.commandLink("auth", "check_login")

        # Alten Usernamen, nach einem Fehlgeschlagenen Login, wieder anzeigen
        username = self.request.form.get("user", "")

        self.session.makeSession() # Eine Session eröffnen

        # Zufallszahl "merken"
        self.session["rnd_login"] = rnd_login

        if debug == True:
            self.session.debug()

        context = {
            "user"          : str(username), #FIXME Unicode <-> str
            "rnd"           : rnd_login,
            "url"           : url
        }

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
            msg = (
                "<h1>Login Error:</h1>"
                "<h3>Form data not complete: '%s'</h3>"
                "<p>Have you enabled JavaScript?</p>"
                "<p>Did you run 'install_PyLucid.py'?"
                " Check login form in SQL table 'pages_internal'.</p>"
            ) % e
            if debug: msg += "CGI-Keys: " + str(self.request.form.keys())
            self.response.write(msg)
            return

        self.check_md5_login(username, form_pass1, form_pass2)


    def _error(self, log_msg, public_msg):
        """Fehler werden abhängig vom Debug-Status angezeigt/gespeichert"""
        self.log(log_msg)

        self.session["isadmin"] = False
        self.session["user"] = False
        # Soll beim commit aktualisiert werden:
        self.session.state = "update session"

        if debug:
            msg = "<p>%s</p><p>Debug: %s</p>" % (public_msg, log_msg)
        else:
            msg = "<p>%s</p>" % public_msg

        raise LogInError(msg)


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
            db_userdata = self.db.md5_login_userdata( username )
        except Exception, e:
            # User exisiert nicht.
            self._error(
                "Error: User '%s' unknown %s" % (username,e) ,
                "User '%s' unknown!" % username
            )
            return

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
        self.page_msg( "You are logged in." )

        # Login/Logout-Link aktualisieren
        self.staticTags.setup_login_link()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True

    #_________________________________________________________________________

    def logout(self):
        self.session.delete_session()
        self.page_msg( "You are logged out." )

        # Damit der Logout-Link zu einem Login-Link wird...
        self.staticTags.setup()

        # Nach dem Ausführen durch den ModuleManager, soll die aktuelle CMS
        # Seite angezeigt werden, ansonsten wäre die Seite leer.
        self.session["render follow"] = True



