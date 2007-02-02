#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid CGI-Session-handler auf Cookie + SQL basis

TODO:
-----
In sessionhandler.read_session() ist ein schneller Work-a-round gemacht, der
anders gelöst werden sollte!
Wir brauchen einen anderen Cookie Handler, der es ermöglicht Cookies zu
löschen und direkt wieder neu zu setzten. Das scheint z.Z. nicht zu gehen.
* Generell muß der cookieHandler aufgeräumt werden!


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev$"


import os, sys, md5, time
from socket import getfqdn
from Cookie import SimpleCookie

try:
    import cPickle as pickle
except ImportError:
    import pickle



#~ debug = True
debug = False

#~ cookie_debug = True
cookie_debug = False

#~ VERBOSE_LOG    = True
VERBOSE_LOG    = False

# Bestimmt den Log-Typ
LOG_TYPE = "sessionhandling"


class cookieHandler:
    def __init__ (self, request, response):
        self.request        = request
        self.response       = response

        # shorthands
        self.URLs           = request.URLs
        self.log            = request.log
        self.page_msg       = response.page_msg
        self.preferences    = request.preferences

        self.CookieName     = "PyLucid_id"

    def getClientID(self):
        """
        Liefert ein existierender Client-ID zurück.
        Wenn noch kein cookie existiert, wird dieser erstellt.
        """
        clientID = self._read_cookie()

        if clientID == False:
            # Kein Cookie vorhanden, also machen wir eins
            clientID = self._gen_clientID()
            self.writeCookie(clientID)

        return clientID


    def _read_cookie(self):
        """ Liest die ID von einem evtl. vorhandenen Cookie """

        if debug:
            self.page_msg( "-"*30 )

        cookie_id = self.readCookie()
        if cookie_id == False:
            # Es gibt kein Session-Cookie, also gibt es keine gültige Session
            msg = "no client cookie found."
            if VERBOSE_LOG == True:
                self.log.write( msg, LOG_TYPE, "error" )
            if debug:
                self.page_msg( msg )
                self.page_msg( "-"*30 )
            return False

        if cookie_id == "":
            self.status = "deleted Cookie found / Client not LogIn!"
            if VERBOSE_LOG==True:
                self.log.write(self.status, LOG_TYPE, "error" )
            return False

        # Testen ob es eine MD5 Checksumme ist
        try:
            if len(cookie_id) != 32:
                raise ValueError
            int(cookie_id, 16) # Ist es eine hex Zahl?
        except ValueError:
            # Mit dem Cookie stimmt wohl was nicht ;)
            self.deleteCookie(self.CookieName)
            msg = "wrong Cookie len: %s !" % len(cookie_id)
            if VERBOSE_LOG == True:
                self.log.write( msg, LOG_TYPE, "error" )
            if debug:
                self.page_msg( msg )
                self.page_msg( "-"*30 )
            return False

        return cookie_id

    def _gen_clientID(self):
        "Generiert eine Session ID anhand der Zeit und der REMOTE_ADDR"
        clientID = md5.new(
            str(time.time()) + self.request.environ["REMOTE_ADDR"]
        ).hexdigest()

        return clientID

    #_________________________________________________________________________
    # Zusätzliche Daten als seperater Cookie

    def set_dataCookie(self, key, value):
        key = self._prepare_cookie_name(key)
        if cookie_debug:
            self.page_msg("Set dataCookie %s with %s" % (key, value))
            self._print_inspect()
        self.response.set_cookie(key, value)

    def get_dataCookie(self, key):
        key = self._prepare_cookie_name(key)
        if cookie_debug:
            self.page_msg("All Cookies:", self.request.cookies)
            self.page_msg("Get '%s' cookie" % key)
            self._print_inspect()
        if not key in self.request.cookies:
            return False
        else:
            return self.request.cookies[key].value

    def del_dataCookie(self, key):
        key = self._prepare_cookie_name(key)
        if cookie_debug:
            self.page_msg("Delete '%s' cookie" % key)
            self._print_inspect()
        self.deleteCookie(key)

    def _prepare_cookie_name(self, key):
        return "%s_%s" % (self.CookieName, key)

    def _print_inspect(self):
        import inspect
        stack = inspect.stack()[2]
        self.page_msg(
            "Cookie action from '...%s' line %s" % (
                stack[1][-30:], stack[2]
            )
        )

    #_________________________________________________________________________
    # Allgemeine Cookie-Funktionen

    def readCookie(self):
        "liest Cookie"
        if not self.CookieName in self.request.cookies:
            return False

        try:
            cookieData = self.request.cookies[self.CookieName].value
        except KeyError:
            return False

        if debug:
            self.page_msg(
                "client cookie '%s' exists: '%s'" % (
                    self.CookieName, cookieData
                )
            )
        return cookieData


    def writeCookie(self, Text, expires=None):
        """
        speichert Cookie
        Es wird kein 'expires' gesetzt, somit ist der Cookie gültig/vorhanden
        bis der Browser beendet wurde.
        """
        #~ if expires==None: expires=self.timeout_sec
        #~ self.Cookie[self.CookieName]["path"] = self.preferences["poormans_url"]
        #~ self.Cookie[self.CookieName]["expires"] = expires

        if self.CookieName in self.request.cookies:
            raise "Existiert schon!"

        if debug:
            self.page_msg( "set_cookie '%s': %s" % (self.CookieName, Text))

        self.response.set_cookie(
            self.CookieName, Text,
        )

        if debug:
            CookieName = self.CookieName
            cookies = self.request.cookies
            try:
                CookieData = cookies[self.CookieName].value
            except KeyError:
                self.page_msg("Can't read cookie")
            else:
                self.page_msg("test Cookie: '%s'" % CookieData)

    def deleteCookie(self, CookieName):
        if debug:
            self.page_msg("delete_cookie '%s'" % CookieName)

        if CookieName in self.request.cookies:
            # FIXME: Bug in colubrid: http://trac.pocoo.org/ticket/34
            # Ist eigentlich auch schon gefixed. Dennoch scheint es nicht
            # zu funktionieren :(
            # Normalerweise sollte es mit response.delete_cookie() gehen!
            #~ self.response.delete_cookie(CookieName)
            # Work-a-round:
            self.response.set_cookie(CookieName, max_age=0)


#_____________________________________________________________________________


class BrokenSessionData(Exception):
    """
    Mit den Session Daten aus der DB stimmt was nicht.
    """
    pass




class sessionhandler(dict):
    """
    CGI-Session Handler
    used mySQL and Cookies

    http://www.python-forum.de/viewtopic.php?p=19523#19523
    """
    __exist_session = False
    __new_session = False

    def init2(self, request, response):
        #~ dict.__init__(self)

        self.request        = request
        self.response       = response

        # shorthands
        self.db             = request.db
        self.log            = request.log
        self.page_msg       = response.page_msg
        self.preferences    = request.preferences
        self.URLs           = request.URLs

        self.sql_tablename  = "session_data"
        self.timeout_sec    = 1800

        self.set_default_values()

        # Client ID ermitteln
        self.cookie = cookieHandler(request, response)
        self["session_id"] = self.cookie.getClientID()

        # Evtl. vorhandene Session-Daten aus DB einlesen
        self.read_session()

        # Daten die erst mit dem sessionhandling verfügbar sind,
        # in das Logging Module übertragen
        self.log.client_sID = self["session_id"]
        self.log.client_user_name = self["user"]
        self.log.client_domain_name = self["client_domain_name"]

    def set_default_values(self):
        """
        Setzt Interne Session-Variable auf voreinstestellte
        'keine-Session-vorhanden-Werte'
        benötigt von:
        self.__init__()
        self.delete_session()
        """
        try:
            self["client_IP"] = self.request.environ["REMOTE_ADDR"]
        except KeyError:
            self["client_IP"] = "unknown"
            self["client_domain_name"] = "[IP Addr. unknown]"
        else:
            try:
                self["client_domain_name"] = getfqdn(self["client_IP"])
            except Exception, e:
                self["client_domain_name"] = "[getfqdn Error: %s]" % e

        self["session_id"] = False
        self["isadmin"] = False
        self["user"] = False

        self.RAW_session_data_len   = -1


    def read_session(self):
        """
        Liest Session-Daten aus der DB
        FIXME: z.Z. wird eine Session erstellt, wenn der User einloggen möchte.
            Das ist auch korrekt so, weil die challenge-Nummer in der DB
            gespeichert werden muß. Nur: Wenn der User doch nicht einloggt,
            dann bleibt die Session aber bestehen. Somit haben
            Suchmaschinen-Bots eine Session, wenn sie einmal auf Login
            kommen :(
        """
        #~ if "auth/login" in self.request.environ["PATH_INFO"]:
            #~ # FIXME: Quick Patch!!!
            #~ # Wenn ein User einloggen will, dann darf der Cookie "has_session"
            #~ # nicht erst vorher gelöscht werden. Danach wird er auch nicht
            #~ # mehr geschrieben!!!
            #~ return

        if debug:
            self.debug()

        isLogin = self.cookie.get_dataCookie("has_session")
        if isLogin != "true":
            # Kein Cookie, dann brauchen wir erst garnicht nachzusehen ;)
            if debug:
                self.page_msg(
                    "No 'is_login == true' Data-Cookie! -> Not login!"
                )
            return

        DB_data = self.read_from_DB(self["session_id"])
        if DB_data == False:
            # Keine Daten in DB
            self.cookie.del_dataCookie("has_session")
            if debug:
                self.page_msg(
                    "No Session data for id %s in DB" % self["session_id"]
                )
            return

        def checkSessiondata(DB_data):
            if DB_data["ip"] != self["client_IP"]:
                msg = "Wrong client IP from DB: %s from Client: %s" % (
                    DB_data["ip"], current_IP
                )
                raise BrokenSessionData, msg

            # Session-Daten auf Vollständigkeit prüfen
            for key in ("isadmin","session_id","user"):
                if not key in DB_data:
                    # Mit den Session-Daten stimmt was nicht :(
                    msg = "Error in Session Data: Key %s not exists." % key
                    raise BrokenSessionData, msg

        try:
            checkSessiondata(DB_data)
        except BrokenSessionData, msg:
            self.log.write(msg, LOG_TYPE, "error")
            if debug:
                self.page_msg(msg)
                self.debug_session_data()
            self.delete_session()
            self.page_msg("Your logged out!")
            return

        # Daten aus der DB in's eigene Dict übernehmen
        self.update(DB_data)

        # Session ist OK
        if VERBOSE_LOG == True or debug == True:
            msg = "Session is OK\nSession-Data %.2fSec old" % (
                time.time()-DB_data["timestamp"]
            )
            if VERBOSE_LOG == True:
                self.log.write(msg, LOG_TYPE, "OK")
            if debug:
                self.page_msg(msg)
                self.debug()

        # Soll beim commit aktualisiert werden:
        self.__exist_session = True


    def makeSession(self):
        """
        Startet eine Session
        """
        if debug:
            self.page_msg("makeSession!")
            self.debug()

        self.cookie.set_dataCookie("has_session", "true")

        # Muß beim commit in die DB eingetragen werden
        self.__new_session = True
        self.__exist_session = True


    def delete_session(self):
        "Löscht die aktuelle Session"
        if debug:
            self.page_msg("-"*30)
            self.page_msg("Delete Session!")
            self.page_msg("debug before:")
            self.page_msg("Cookies:", self.request.cookies)
            self.debug_session_data()

        self.cookie.del_dataCookie("has_session")

        # Interne-Session-Variablen rücksetzten
        self.__exist_session = None
        self.__new_session = None
        self["isadmin"] = False
        self["user"] = False

        if self["session_id"] == False:
            self.status = (
                "OK;Client is LogOut, can't LogOut a second time :-)!"
            )
            if debug:
                self.page_msg(
                    "session_id is false, can't delete session in db."
                )
            return

        self.db.delete(
            table = self.sql_tablename,
            where = ("session_id",self["session_id"])
        )

        if debug:
            self.page_msg("debug after:")
            self.page_msg("Cookies:", self.request.cookies)
            self.debug_session_data()
            self.page_msg("-"*30)

        self.status = (
            "OK;delete Session data / LogOut for '%s'"
        ) % self["session_id"]

    def commit(self):
        """
        Schreibt die aktuellen Sessiondaten in die DB.
        Sollte also immer als letztes Aufgerufen werden ;)
        """
        if debug:
            self.page_msg("session.commit()")

        if self.__exist_session != True and self.__new_session != True:
            # Es gibt nichts zu tun ;)
            if debug:
                self.page_msg("no session.commit() needed.")
            return

        if self["session_id"] == False:
            self.page_msg("session_id == False!!!")
            return

        if self.__new_session:
            # Es ist eine neue Session die in der DB erst erstellt werden muß

            # Evtl. vorhandene Daten löschen
            self.db.delete(
                table = self.sql_tablename,
                where = ("session_id", self["session_id"]),
            )

            session_data = self._prepare_sessiondata()
            self.db.insert(
                table = self.sql_tablename,
                data  = {
                    "session_id"    : self["session_id"],
                    "timestamp"     : time.time(),
                    "ip"            : self["client_IP"],
                    "domain_name"   : self["client_domain_name"],
                    "session_data"  : session_data,
                }
            )
            self.db.commit()

            self.log.write( "created Session.", LOG_TYPE, "OK" )
            if debug:
                self.page_msg("insert session data for:", self["session_id"])
                self.debug_session_data()

        elif self.__exist_session:
            session_data = self._prepare_sessiondata()
            self.db.update(
                table   = self.sql_tablename,
                data    = {
                    "session_data"  : session_data,
                    "timestamp"     : time.time()
                },
                where   = ("session_id", self["session_id"]),
                limit   = 1,
            )
            self.db.commit()

            if VERBOSE_LOG == True:
                self.log.write(
                    "update Session: ID:%s" % self["session_id"],
                    LOG_TYPE, "OK"
                )
            if debug:
                self.page_msg("update Session: ID:%s" % self["session_id"])
                self.debug_session_data()
        else:
            self.page_msg.red("Unknown session error!!!")

        if debug:
            self.debug()

    def _prepare_sessiondata(self):
        session_data = dict(self) # Kopie des Dict's machen

        # "doppelte" Keys löschen:
        del(session_data["session_id"])
        del(session_data["client_IP"])
        del(session_data["client_domain_name"])

        session_data = pickle.dumps(session_data, pickle.HIGHEST_PROTOCOL)
        self.RAW_session_data_len = len(session_data)

        return session_data

    #_________________________________________________________________________
    # Allgemeine SQL-Funktionen

    def read_from_DB(self, session_id):
        "Liest Sessiondaten des Users mit der >session_id<"
        self._delete_old_sessions() # Löschen veralteter Sessions in der DB

        DB_data = self.db.select(
                select_items    = [
                    "session_id", "timestamp", "ip",
                    "domain_name", "session_data"
                ],
                from_table      = self.sql_tablename,
                where           = ("session_id",session_id)
            )
        if DB_data == []:
            return False

        #~ if debug: self.page_msg( "DB_data:",DB_data )
        if len(DB_data) > 1:
            "More than one Session in DB! (%s session found!)" % len(DB_data)
            self.page_msg(msg)
            self.log.write(msg, "sessionhandling", "error")
            return False

        DB_data = DB_data[0]

        sessionData = DB_data["session_data"]
        del(DB_data["session_data"])

        self.RAW_session_data_len = len(sessionData)

        # Aus der DB kommt ein array Objekt!
        sessionData = sessionData.tostring()
        try:
            sessionData = pickle.loads(sessionData)
        except Exception, e:
            self.page_msg("Can't read sessiondata: %s" % e)
            self.debug_session_data()
            return False

        DB_data.update(sessionData)

        return DB_data


    def _delete_old_sessions(self):
        "Löscht veraltete Sessions in der DB"
        SQLcommand  = "DELETE FROM $$%s" % self.sql_tablename
        SQLcommand += " WHERE timestamp < ?"

        current_timeout = time.time() - self.timeout_sec

        if debug:
            self.page_msg("-"*30)
            self.page_msg("Delete old Sessions!")
            self.page_msg("SQLcomand:", SQLcommand, current_timeout)
            self.page_msg("debug before:")
            self.debug_session_data()

        try:
            self.db.cursor.execute(SQLcommand, (current_timeout,))
        except Exception, e:
            msg = "Content-type: text/html\n"
            msg += "Delete Old Session error: %s" % e
            self.page_msg(msg)
            sys.stderr.write(msg)
            sys.exit()

        if debug:
            self.page_msg("debug after:")
            self.debug_session_data()
            self.page_msg("-"*30)

    #_________________________________________________________________________

    def debug_session_data(self):
        if VERBOSE_LOG != True:
            return

        import inspect
        stack_info = inspect.stack()[2][4][0]

        try:
            RAW_db_data = self.db.select(
                select_items    = ['timestamp', 'session_data','session_id'],
                from_table      = self.sql_tablename,
                where           = [("session_id",self["session_id"])]
            )
            self.page_msg(
                "Debug from %s: %s<br />" % (stack_info, RAW_db_data)
            )
        except Exception, e:
            self.page_msg( "Debug-Error from %s: %s" % (stack_info,e) )
            #~ for i in inspect.stack(): self.page_msg( i )

    #_________________________________________________________________________
    ## Debug

    def debug(self):
        "Zeigt alle Session Informationen an"

        import inspect
        # PyLucid's page_msg nutzen
        self.page_msg( "-"*30 )
        self.page_msg(
            "Session Debug (from '%s' line %s):" % (
                inspect.stack()[1][1][-20:], inspect.stack()[1][2]
            )
        )

        self.page_msg("self.__exist_session:", self.__exist_session)
        self.page_msg("self.__new_session:", self.__new_session)

        self.page_msg("len:", len(self))
        for k,v in self.iteritems():
            self.page_msg( "%s - %s" % (k,v) )
        self.page_msg("ID:", self["session_id"])
        self.page_msg( "-"*30 )

    def debug_last(self):
        """ Zeigt die letzten Einträge an """
        import inspect
        self.page_msg(
            "Session Debug (from '%s' line %s):" % (
                inspect.stack()[1][1][-20:], inspect.stack()[1][2]
            )
        )
        info = self.db.select( ["timestamp","session_id"], "session_data",
            limit=(0,5),
            order=("timestamp","DESC"),
        )
        for item in info:
            self.page_msg(item)

    #_________________________________________________________________________
    ## Spezielle PyLucid Methoden

    def _forced_fake_login(self):
        """
        FOR TEST ONLY!
        Wenn man am auth system rumbastelt, ist es manchmal hilfreich einfach
        immer eingeloggt zu sein.
        """
        self.page_msg.red("WARNING: forced fake login is ON!")
        self["isadmin"] = True
        self["user_id"] = -1
        self["user"] = "fake login"


    def set_pageHistory(self, page_id):
        """
        Seite zur page_history hinzufügen
        """
        if not "page_history" in self or \
                                not isinstance(self["page_history"], list):
            self["page_history"] = [page_id]
            return

        # Aktuelle Seite einfügen:
        self["page_history"].insert(0, page_id)

        # Auf letzten 10 limitieren:
        self["page_history"] = self["page_history"][:10]


    def delete_from_pageHistory(self, page_id):
        self["page_history"] = [i for i in self["page_history"] if i!=page_id]

        if self["page_history"]==[]:
            self["page_history"]=[self.preferences["core"]["defaultPage"]]




