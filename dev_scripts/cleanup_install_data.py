#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Delete dump_db files not needed for a first-time-installation.
"""

import os, sys
os.chdir("../pylucid_project/") # go into PyLucid App root folder
#print os.getcwd()
sys.path.insert(0, os.getcwd())

from PyLucid import settings



SIMULATE = True
#SIMULATE = False
PREFIX = "PyLucid_"


# DB data files not needed for installation
UNNEEDED_FILES = (
    "plugin", "plugindata", "pagesinternal",
    "preference", "js_logindata", "pagearchiv"
)




def delete_file(path):
        print "delete '%s'" % filename,
        if SIMULATE:
            print "[simulate only]",
        else:
            os.remove(abs_path)
        print "OK\n"

filelist = os.listdir(settings.INSTALL_DATA_DIR)

prefix_len = len(PREFIX)
filelist.sort()
for filename in filelist:
    if filename.startswith("."):
        # e.g. .svn
        continue

    abs_path = os.path.join(settings.INSTALL_DATA_DIR, filename)

    if not filename.startswith(PREFIX):
        # django tables
        delete_file(abs_path)
        continue

    # Cut prefix and externsion out
    fn_cut = filename[prefix_len:-3]
#    print fn_cut
    if fn_cut in UNNEEDED_FILES:
        delete_file(abs_path)
        continue

    print "needed file:", filename
    print
