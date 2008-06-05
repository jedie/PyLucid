# -*- coding: utf-8 -*-

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "simple page counter"
__long_description__ = """
A simple page counter.

Usage: Put the tag {% lucidTag page_counter %} into your template.
On every non-cached view of the page, the counter will increase and the tag
retuns the total number of views of this page.

Note: Counts not cached views!
"""
#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
