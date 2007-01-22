#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
show internals - Python modules info

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev:$"


import os, sys, imp, glob


class PythonModuleInfo(object):
    """
    Auflisten aller installierten Module
    """
    def __init__( self ):
        self.glob_suffixes = self.get_suffixes()

        filelist = self.scan()
        self.modulelist = self.test( filelist )

    def get_suffixes( self ):
        """
        Liste aller Endungen aufbereitet für glob()
        """
        suffixes = ["*"+i[0] for i in imp.get_suffixes()]
        suffixes = "[%s]" % "|".join(suffixes)
        return suffixes

    def get_files( self, path ):
        """
        Liefert alle potentiellen Modul-Dateien eines Verzeichnisses
        """
        files = []
        for suffix in self.glob_suffixes:
            searchstring = os.path.join( path, suffix )
            files += glob.glob(searchstring)
        return files

    def scan( self ):
        """
        Verzeichnisse nach Modulen abscannen
        """
        filelist = []
        pathlist = sys.path
        for path_item in pathlist:
            if not os.path.isdir( path_item ):
                continue

            for file in self.get_files( path_item ):
                file = os.path.split( file )[1]
                if file == "__init__.py":
                    continue

                filename = os.path.splitext( file )[0]

                if filename in filelist:
                    continue
                else:
                    filelist.append( filename )

        return filelist

    def test( self, filelist ):
        """
        Testet ob alle gefunden Dateien auch als Modul
        importiert werden können
        """
        modulelist = []
        for filename in filelist:
            if filename == "": continue
            try:
                imp.find_module( filename )
            except:
                continue
            modulelist.append( filename )
        return modulelist