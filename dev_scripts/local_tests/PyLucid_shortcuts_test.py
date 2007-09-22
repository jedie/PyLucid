#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO: Should be rewritten to a real shortcut unittest!!!
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True
)

#______________________________________________________________________________
# Test:

from PyLucid.models import Page

print "List of all Pages:"
for page in Page.objects.all():
    print " * %s" % page
    print "   ->", page.get_absolute_url()
    print