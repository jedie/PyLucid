#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
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
print

page = Page.objects.all()[0]
shortcut = page.shortcut

print "Filter shortcut: '%s':" % shortcut

id = page.id
print "XXX:", Page.objects.get(id=id).shortcut

shortcuts = Page.objects.values("shortcut").exclude(shortcut=shortcut)

shortcuts = [i["shortcut"] for i in shortcuts]
print shortcuts

print "-----------------------------------------------------------------------"

page = Page.objects.all()[0]

print "Build a list of all model field names:"
fields = []
for field in page._meta.fields:
#    print field
    field_name = field.column.replace('_id','')
    fields.append(field_name)

print fields