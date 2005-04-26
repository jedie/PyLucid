#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verschiedene Tools f�r den Umgang mit lucid
"""

__version__="0.0.2"

"""History
v0.0.2
    - einbindung der preferences
v0.0.1
    - erste Version
"""

import time, sys, re, htmlentitydefs


import config, preferences









class convertdateformat:
    """
    Wandelt das PHP-date Format in's Python-Format
    z.B. PHP-date "j.m.Y G:i" -> "%d.%m.%Y - %H:%M"

    PHP-Format:
    selfphp.info/funktionsreferenz/datums_und_zeit_funktionen/date.php#beschreibung

    Python-Format:
    docs.python.org/lib/module-time.html#l2h-1941

    nicht eingebaute PHP-Formate:
    --------------------------------------------------------------------
    B - Tage bis Jahresende
    I - (großes i) 1 bei Sommerzeit, 0 bei Winterzeit
    L - Schaltjahr = 1, kein Schaltjahr = 0
    O - Zeitunterschied gegenüber Greenwich (GMT) in Stunden (z.B.: +0100)
    r - Formatiertes Datum (z.B.: Tue, 6 Jul 2004 22:58:15 +0200)
    S - Englische Aufzählung (th für 2(second))
    t - Anzahl der Tage des Monats (28 – 31)
    T - Zeitzoneneinstellung des Rechners (z.B. CEST)
    U - Sekunden seit Beginn der UNIX-Epoche (1.1.1970)
    Z - Offset der Zeitzone gegenüber GTM (-43200 – 43200) in Minuten

    nicht eingebaute Python-Formate:
    --------------------------------------------------------------------
    %c 	Locale's appropriate date and time representation.
    %x 	Locale's appropriate date representation.
    %X 	Locale's appropriate time representation.
    %Z 	Time zone name (no characters if no time zone exists).
    """
    def __init__( self ):
        self.PHP2Python_date = {
            "d" : "%d", # Tag des Monats *( 01 – 31 )
            "j" : "%d", # Tag des Monats (1-31)
            "D" : "%a", # Tag der Woche (3stellig:Mon)
            "l" : "%A", # Tag der Woche (ausgeschrieben:Monday)

            "m" : "%m", # Monat *(01-12)
            "n" : "%m", # Monat (1-12)
            "F" : "%B", # Monatsangabe (December – ganzes Wort)
            "M" : "%b", # Monatsangabe (Feb – 3stellig)

            "y" : "%y", # Jahreszahl, zweistellig (01)
            "Y" : "%Y", # Jahreszahl, vierstellig (2001)

            "g" : "%I", # Stunde im 12-Stunden-Format (1-12 )
            "G" : "%H", # Stunde im 24-Stunden-Format (0-23 )
            "h" : "%I", # Stunde im 12-Stunden-Format *(01-12 )
            "H" : "%H", # Stunde im 24-Stunden-Format *(00-23 )
            "i" : "%M", # Minuten *(00-59)
            "s" : "%S", # Sekunden *(00 – 59)

            "a" : "%p", # "am" oder "pm"
            "A" : "%p", # "AM" oder "PM"

            "w" : "%w", # Wochentag als Zahl (0(Sonntag) bis 6(Samstag))
            "W" : "%W", # Wochennummer des Jahres (z.B. 28)
            "z" : "%j"  # Tag des Jahres als Zahl (z.B. 148 (entspricht 29.05.2001))
        }

    def convert( self, formatDateTime ):
        "PHP-date Format in Python-Format umwandeln"

        for item in re.findall(r"\w", formatDateTime ):
            formatDateTime = formatDateTime.replace( item, self.PHP2Python_date[item] )

        return formatDateTime

#~ formatDateTime = "j.m.Y G:i"
#~ print formatDateTime
#~ formatDateTime = convertdateformat().convert( formatDateTime )
#~ print formatDateTime
#~ sys.exit()




def date( RAWsqlDate ):
    """
    Wandelt ein Datum aus der SQL-Datenbank in ein Format, welches
    in lucid unter "config/core/DateTime Format" festgelegt wurde.
    """
    formatDateTime = config.preferences["core"]["formatDateTime"]
    formatDateTime = convertdateformat().convert( formatDateTime )

    date = str( RAWsqlDate )
    try:
        # Dateum in's Python Format parsen
        date = time.strptime( date, "%Y-%m-%d %H:%M:%S" )
    except ValueError:
        # Datumsformat stimmt nicht, aber besser das was schon da
        # ist, mit einem Hinweis, zurück liefern, als garnichts ;)
        return "ERROR:"+date

    # Datum in einem String wandeln
    date = time.strftime( formatDateTime, date ) # formatDateTime
    return date

#~ import config, preferences, SQL
#~ print date( "2005-04-21 12:27:03" )
#~ sys.exit()