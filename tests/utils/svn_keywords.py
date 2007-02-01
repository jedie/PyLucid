#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" PyLucid SVN tool

    - sync svn:keywords


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$
$HeadURL:$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import os, sys, re

try:
    import pysvn
except ImportError, e:
    print "Import Error: ", e
    print "You must install pysvn from:"
    print "http://pysvn.tigris.org"
    sys.exit()


#_____________________________________________________________________________
# settings:

REPOSITORY = "../../" # PyLucid trunk Verz.

#~ SIMULATION = False
SIMULATION = True

# Dateien die keine svn:keywords haben dÃ¼rfen, ist in den svn:keywords dennoch
# welche drin, werden die gelÃ¶scht:
NO_KEYWORD_FILE_EXT = (".zip",)

# Dateien mit der Endung, werden komplett ausgelassen:
SKIP_FILE_EXT = (".pyc",)

ALLOWED_KEYWORDS = set([
    "LastChangedDate", "LastChangedRevision", "LastChangedBy", "HeadURL",
    "Id", "Rev", "Author"
])

#_____________________________________________________________________________


client = pysvn.Client()

# Hier ist $ durch \x24 maskiert, damit das Skript nicht die re findet!
re_keywords = re.compile(r"\x24(.*?):(.*?)\x24")

# Ein kleiner Test fÃ¼r die re:
assert re_keywords.findall(u"jau\u0024Test:OK\u0024jup") == [(u'Test', u'OK')]


#_____________________________________________________________________________

def cleanup():
    print "SVN cleanup...",
    client.cleanup(REPOSITORY)
    print "OK"

#_____________________________________________________________________________


def print_status():
    """
    shows the SVN status
    """
    def print_list(changes, status):
        print "%s files:" % status
        wc_status = getattr(pysvn.wc_status_kind, status)
        count = 0
        for f in changes:
            if f.text_status != wc_status:
                continue
            count +=1
            print "    ", f.path
        print "  %s file(s)" % count

    print "SVN status:"
    print "- "*39
    changes = client.status(REPOSITORY)

    for status in ("added","deleted","modified","conflicted","unversioned"):
        print_list(changes, status)

    print "- "*39

#_____________________________________________________________________________

def walk():
    """
    os.walk durch das repro-Verz.
    Liefert den absoluten Pfad als generator zurí¤«
    """
    for dir,_,files in os.walk(REPOSITORY):
        if ("/.svn" in dir) or ("\\.svn" in dir):
            # Versteckte .svn Verzeichnisse auslassen
            continue

        for fn in files:
            ext = os.path.splitext(fn)[1]
            if ext in SKIP_FILE_EXT:
                continue
            abs_path = os.path.join(dir, fn)
            yield abs_path

#_____________________________________________________________________________

def get_file_keywords(fn):
    """
    Fischt aus dem DateiInhalt vorhandene keywords per re raus
    """
    f = file(fn, "r")
    content = f.read()
    f.close()

    keywords = re_keywords.findall(content)
    if keywords == []:
        return set()

    return set([i[0] for i in keywords])

def get_svn_keywords(proplist):
    """
    Liefert eine set() der vorhanden svn:keywords zurí¤«.
    proplist = pysvn.Client().proplist(filename)
    """
    try:
        props = proplist[0][1]["svn:keywords"]
    except (IndexError, KeyError):
        # Hat keine keywords
        return set()
    else:
        return set(props.split(" "))

#_____________________________________________________________________________

def delete_svn_keywords(filename, proplist):
    """
    Lç´£ht aus den svn-properties den Eintrag "svn:keywords", wenn vorhanden.
    """
    svn_keywords = get_svn_keywords(proplist)
    if len(svn_keywords) == 0:
        # Hat keine Keywords die man lç´£hen kç¯®te
        print "File has no svn:keywords, OK"
        return

    print ">>>", svn_keywords
    print "Delete svn_keywords"

    client.propdel("svn:keywords", filename)

def set_svn_keywords(filename, keywords):
    """
    Setzt svn:keywords
    """
    keywords = " ".join(keywords)
    print ">>> set svn_keywords to:", keywords
    if SIMULATION:
        print "simulation on, no change made."
        return

    client.propset("svn:keywords", keywords, filename)

#_____________________________________________________________________________

def sync_keywords():
    """
    syncronisiert keywords aus allen Dateien.
    """
    for fn in walk():
        try:
            svn_entry = client.info(fn)
        except pysvn._pysvn.ClientError, e:
            if "is not a working copy" in str(e):
                # ist nicht in repository
                pass
            else:
                print ">>> Error:", e
            continue
        else:
            if svn_entry == None:
                # Die Datei ist nicht im repository
                continue

        print "-"*40
        print fn

        proplist = client.proplist(fn)

        ext = os.path.splitext(fn)[1]
        if ext in NO_KEYWORD_FILE_EXT:
            # Diese Datei sollte keine Keywords haben!
            delete_svn_keywords(fn, proplist)
            continue

        file_keywords = get_file_keywords(fn)

        if not file_keywords.issubset(ALLOWED_KEYWORDS):
            print ">>>Error!"
            not_allowed = file_keywords.difference(ALLOWED_KEYWORDS)
            print ">Found not allowed keyword in file:", ", ".join(not_allowed)
            file_keywords = file_keywords.intersection(ALLOWED_KEYWORDS)
            print ">I used only this keywords:", ", ".join(file_keywords)

        svn_keywords = get_svn_keywords(proplist)

        print "keywords in file..: >%s<" % " ".join(sorted(file_keywords))
        print "svn:keywords......: >%s<" % " ".join(sorted(svn_keywords))

        if file_keywords != svn_keywords:
            print "keywords are different -> change it:"
            if len(file_keywords) == 0:
                delete_svn_keywords(fn, proplist)
            else:
                set_svn_keywords(fn, list(file_keywords))
        else:
            print "keywords are the same, ok"


#_____________________________________________________________________________


if __name__ == "__main__":
    cleanup()
    sync_keywords()
    print_status()