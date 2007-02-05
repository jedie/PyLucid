#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" PyLucid SVN tool - sync svn:keywords

Used svn_keyword.py from:

http://pylucid.net/trac/browser/CodeSnippets/svn_keyword.py
or
http://svn.pylucid.net/pylucid/CodeSnippets/svn_keyword.py

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev: $
$Author: $
$HeadURL: $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import sys, os

sys.path.insert(0,"../../../CodeSnippets/")

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
config.repository = "." # PyLucid trunk Verz.
#~ config.simulation = False
config.simulation = True


if __name__ == "__main__":
    os.chdir("../../")
    cleanup(config)
    sync_keywords(config)
    print_status(config)