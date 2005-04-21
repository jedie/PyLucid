#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verschiedene Tools für den Umgang mit lucid
"""

__version__="0.0.1"


import time, sys


import config


PHP2Python_date = {
    "j" : "%d",
    "m" : "%m",
    "Y" : "%Y",
    "G" : "%H",
    "i" : "%M"
}


def date( RAWsqlDate ):
    """
    Wandelt ein Datum aus der SQL-Datenbank in ein Format, welches
    in lucid unter "config/core/DateTime Format" festgelegt wurde.
    """
    # lucid bzw. PHP-date Format in Python-Format umwandeln
    formatDateTime = config.preferences["core"]["formatDateTime"]
    for php,py in PHP2Python_date.iteritems():
        formatDateTime = formatDateTime.replace( php,py )

    date = str( RAWsqlDate )
    try:
        # Dateum in's Python Format parsen
        date = time.strptime( date, "%Y-%m-%d %H:%M:%S" )
    except ValueError:
        # Datumsformat stimmt nicht, aber besser das was schon da
        # ist, mit einem Hinweis, zurÃ¼ck liefern, als garnichts ;)
        return "ERROR:"+date

    # Datum in einem String wandeln
    date = time.strftime( formatDateTime, date ) # formatDateTime
    return date

#~ print date( "2005-04-21 12:27:03" )
#~ sys.exit()