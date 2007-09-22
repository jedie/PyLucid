#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid svn:keywords sync tool
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    usefull tools to automatic setup the SVN keywords.

    Used svn_keyword.py from:

    http://pylucid.net/trac/browser/CodeSnippets/svn_keywords.py
    or
    http://svn.pylucid.net/pylucid/CodeSnippets/svn_keywords.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, os

os.chdir("../") # go into PyLucid App root folder
print os.getcwd()

# Path to the svn_keywords.py file:
sys.path.insert(0,"../CodeSnippets/")

try:
    from svn_keywords import Config, cleanup, print_status, sync_keywords
except ImportError, e:
    print "Error, can't import svn_keywords.py:"
    print e
    print
    print "(More Information in Doc-String)"
    print
    sys.exit()

config = Config
config.repository = "." # PyLucid
config.skip_dirs = (
    "./django", "./pygments",
    "./PyLucid/db_dump_datadir/",
    "./media/PyLucid/tiny_mce",
)
config.skip_file_ext = (".pyc",".gif", ".png")
#config.simulation = False
config.simulation = True


if __name__ == "__main__":
#    cleanup(config)
    sync_keywords(config)
#    print_status(config)


