#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verallgemeinert einen PyLucid SQL-Dump
damit er zur erst installation taugt ;)
    - Tauscht den Tabellen-Prefix-String mit Python's String Formatting Operator
    - Filtert unnötige Informationen (Archiv, Session-Daten, User-Passwörter)
    - erstellt eine ZIP-Datei mit den relevaten SQL-Daten
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - Erste Version
"""


import os, sys, re, time, zipfile, zlib

zlib.Z_DEFAULT_COMPRESSION = 9


infilename      = "20051006_lucid_DatabaseName 2.sql"
#~ TablePrefix     = "PyLucid_base_"
TablePrefix     = "lucid_"

# Diese Angaben müßen mit den in der install_PyLucid.py übereinstimmen!
outfilename     = "PyLucid_SQL_install_data.zip"
zip_filename    = "SQLdata.sql"


# Einträge die rausfallen
filter_startswith = (
    "INSERT INTO `%(table_prefix)sarchive`",
    "INSERT INTO `%(table_prefix)slog`",
    "INSERT INTO `%(table_prefix)smd5users`",
    "INSERT INTO `%(table_prefix)ssession_data`",
    "INSERT INTO `%(table_prefix)susers`",
    "INSERT INTO `%(table_prefix)suser_group`",

    "LOCK TABLES",
    "UNLOCK TABLES",
)

# Filter für zusätzliche SQL-Angaben im CREATE TABLE statement
pattern = "[^;, ]* *"
crate_table_filters = (
    "collate %s" % pattern,
    "ENGINE=%s" % pattern,
    "COLLATE=%s" % pattern,
    "character set %s" % pattern,
    "DEFAULT CHARSET=%s" % pattern,
)

cleaning_filters = (
    "/\*.*?\*/;",
)

class universalize_dump:
    def __init__( self ):
        self.in_create_table = False
        self.after_commend = False
        self.found_dbprefix = False

        self.check_file( outfilename )
        self.process()

    def check_file( self, filename ):
        if os.path.isfile( filename ):
            print "File '%s' exists, try to delete..." % filename,
            try:
                os.remove( filename )
            except Exception, e:
                print "fail:", e
                sys.exit()
            else:
                print "OK"


    def process( self ):
        """
        DUMP-Daten Konvertieren und in ZIP Datei schreiben
        """
        print "Read Data and convert...",
        infile = file( infilename, "rU" )

        re_find_name = re.compile( r"`\%\(table_prefix\)s(.*?)`" )
        category = ""
        outdata = { "info.txt": self.dump_info() }
        #~ in_create_table = False

        for line in infile:
            line = self.preprocess( line )
            if line.startswith("--"):
                category = "info.txt"
            else:
                find_name = re_find_name.findall( line )
                if find_name != []:
                    category = find_name[0]+".sql"

            if category != "info.txt" and (not line.endswith(";\n")):
                # Jedes SQL-Kommando in einer Zeile quetschen
                line = line[:-1].strip()

            if not outdata.has_key(category):
                outdata[category] = ""

            if line=="": continue # Leere Zeilen brauchen wir nicht

            outdata[category] += line

        infile.close()
        print "OK"

        print "Write zipfile...",
        outfile = zipfile.ZipFile( outfilename, "w", zipfile.ZIP_DEFLATED)
        for filename,data in outdata.iteritems():
            outfile.writestr(filename,data)
        outfile.close()
        print "OK"

        print

        if self.found_dbprefix == False:
            print "ERROR: No table prefix '%s' found!!!" % TablePrefix

    def dump_info( self ):
        """
        Informationen die im SQL Dump eingeblendet werden
        """
        txt  = "-- ------------------------------------------------------\n"
        txt += "-- universalized %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"), os.path.split(__file__)[1], __version__
        )
        return txt

    def preprocess( self, line ):
        """
        -Filterung des aktuellen Tableprefix nach %(table_prefix)s
        -Einblendung der Dump-Informationen
        """
        # Prozentzeichen escapen
        line = line.replace( "%", "%%" )
        prefix_mark = "`%s" % TablePrefix

        # Tabellen Prefixe ändern
        if prefix_mark in line:
            self.found_dbprefix = True
            line = line.replace( prefix_mark, "`%(table_prefix)s" )

        # Zeilen filtern
        for filter in filter_startswith:
            if line.startswith( filter ):
                return ""

        # Spezielle SQL Kommandos rausschmeißen
        #~ if line.startswith( "/*" ) and line.endswith( "*/;\n" ):
            #~ print ">", line
            #~ return ""

        if line.startswith( "CREATE TABLE" ):
            self.in_create_table = True

        if self.in_create_table == True:
            #~ print line[:-1]
            for filter in crate_table_filters:
                line = re.sub( filter, "", line )
            #~ print ">",line

        if line.endswith( ";\n" ):
            self.in_create_table = False

        for filter in cleaning_filters:
            line = re.sub( filter, "", line )

        return line


if __name__ == "__main__":
    universalize_dump()