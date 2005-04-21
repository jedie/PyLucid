#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einstellungen von lucid lesen
=============================

1. Liest die SQL-Konfiguration mittels dbconfig.py

2. Holt die Einstellungen aus der Tabelle preferences
    und speichert die in config.preferences
"""

__version__="0.0.1"

import os, re

import config, SQL


class preferences:
    """
    lucid-preferences in der Datenbank
    """

    def __init__( self ):
        self.putCFGtoConfig( self.getCFG() )

    def getCFG( self ):
        """
        Liest die preferences aus der Datenbank aus
        """

        SQLcommand = """SELECT `section` , `varName` , `value`
        FROM `%(prefix)spreferences`
        """ % {
            "prefix" : config.dbconf["dbTablePrefix"]
        }

        db = SQL.db()
        db.execute( SQLcommand )
        return db.fetchall()

    def putCFGtoConfig( self, SQLresult ):
        """
        Parsed den SQL-Result-Tuple und schreibt die Daten
        sinnvoll in config.preferences
        """
        for line in SQLresult:
            #~ print line
            section = line[0]
            varName = line[1]
            value = line[2]

            if not config.preferences.has_key( section ):
                config.preferences[section] = {}

            config.preferences[section][varName] = value


    def dump_preferences( self ):
        """
        Listet die Einstellungen aus config.preferences auf
        """
        for section in config.preferences:
            print "\nsection: %s" % section
            print "-"*80
            for varName in config.preferences[section]:
                value = config.preferences[section][varName]
                print "%s: '%s'" % (
                    varName,
                    value
                )





##########################################
## Anmerkung zu Pythons Reg.Expressions ##
##########################################
# . beliebiges Zeichen
# ˆ Zeilenanfang (funktioniert nur mit re.MULTILINE)
# $ Zeilenende
#
# \A Textanfang
# \Z Textende
# \b Wortgrenze
# \B nicht Wortgrenze
#
# * beliebig oft
# + beliebig oft, mindestens 1 mal
# | Alternative
# ? Optional
#
# {3,}      Zeichen ab drei Stück hintereinander
# {1,2}     Zeichen von ein bis zwei
#
# \d        Dezimalziffern [0-9]
# \s        Leerzeichen jeder Art [ \t\n\r\f\v]
# \w        alphanumerische Zeichen [a-zA-Z0-9_]
#
# (?m)      Schaltet re.MULTILINE ein
# (?s)      Schaltet re.SINGLELINE ein



class dbcfg:
    """
    Datenbank-Einstellungen aus der "dbConfig.php"
    Der richtige Pfad zur Datei wird in config.system.PHPdbconfig
    festgelegt!
    """
    def __init__( self ):
        if os.environ.has_key('DOCUMENT_ROOT'):
            DocRoot = os.environ['DOCUMENT_ROOT']
        else:
            # Es wird wohl ein lokaler Test gefahren. In dem Falle
            # werden die Default Werte in config.dbconf genutzt
            return

        PHPdbconfig = os.path.join( DocRoot, config.system.PHPdbconfig )

        f = file( PHPdbconfig, "r" )
        self.parsecfg( f.read() )
        f.close()

    def parsecfg( self, cfg ):
        for line in cfg.split():
            parsed = re.search( r"""\$(?P<key>.+?)=['"](?P<value>.+?)['"]""", line )
            if parsed == None:
                continue
            parsed = parsed.groupdict()

            # In die globale config schreiben
            config.dbconf[ parsed["key"] ] = parsed["value"]



def getcfg():
    """
    Einstellungen von lucid lesen
    """
    # SQL-Konfig einlesen und in config.dbconf schreiben
    dbcfg()
    # Die preferences aus der Datenbank auslesen
    preferences()


# und los geht's
getcfg()


if __name__ == "__main__":
    # Lokaler Test
    preferences().dump_preferences()