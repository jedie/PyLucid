#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup the environment for the "local_dev_tests".
"""

# Go into the root folder and insert it into the sys.path
import os, sys
#print "os.getcwd() 1:", os.getcwd()
os.chdir("../unittests")
#print "os.getcwd() 2:", os.getcwd()
sys.path.insert(0, os.getcwd())

# make setup available
from setup_environment import setup

if __name__ == "__main__":
    print "Local Test:"
    setup()

    print "-"*80
    from PyLucid.models import Page
    print "Existing pages:"
    for page in Page.objects.all():
        print " *", page

    print "END"