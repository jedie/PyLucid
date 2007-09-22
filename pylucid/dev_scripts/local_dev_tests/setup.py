#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup the environment for the "local_dev_tests".
"""

# Go into the root folder and insert it into the sys.path
import os, sys
os.chdir("../../")
#print "os.getcwd():", os.getcwd()
sys.path.insert(0, os.getcwd())

# make setup available
from dev_scripts.unittests.setup_environment import setup