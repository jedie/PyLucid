#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" Some Formatter

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

def filesizeformat(i):
    """
    Taken from jinja, by Armin Ronacher, Georg Brandl

    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))


def formatter( number, format="%0.2f", comma=",", thousand=".", grouplength=3):
    """
    Formatierung für Zahlen
    s. http://www.python-forum.de/viewtopic.php?t=371
    Ist schneller als: locale.format("%.2f",number,1)
    und funktioniert auch, wenn die locales auf dem Betriebssystem nicht
    richtig installiert/konfiguriert sind.
    """
    if abs(number) < 10**grouplength:
        return (format % (number)).replace(".", comma)
    if format[-1]=="f":
        vor_komma,hinter_komma=(format % number).split(".",-1)
    else:
        vor_komma=format % number
        comma=""
        hinter_komma=""
    #Hier
    anz_leer=0
    for i in vor_komma:
        if i==" ":
            anz_leer+=1
        else:
            break
    vor_komma=vor_komma[anz_leer:]
    #bis hier

    len_vor_komma=len(vor_komma)
    for i in range(grouplength,len_vor_komma+(len_vor_komma-1)/(grouplength+1)-(number<0),grouplength+1):
        vor_komma=vor_komma[0:-(i)]+thousand+vor_komma[-(i):]
    return anz_leer*" "+vor_komma+comma+hinter_komma