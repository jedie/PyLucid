#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Backport for some Python v2.4 features

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


import sys, __builtin__

# Damit subprocess.py usw. gefunden werden:
sys.path.insert(0,"PyLucid/python_backports")

if not "set" in dir(__builtin__):
    # set und frozenset - nutz das original sets.py aus Python 2.4
    from sets import Set, ImmutableSet
    __builtin__.set = Set
    __builtin__.frozenset = ImmutableSet

