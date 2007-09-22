#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=False
)

#______________________________________________________________________________
# Test:

from django.db.models import get_apps, get_models

for app in get_apps():
    print "%s:" % app.__name__
    for model in get_models(app):
        print " * %s" % model._meta.object_name

    print


#from PyLucid.models import Plugin, Markup, PagesInternal
#
#plugin = Plugin.objects.create()
#print "plugin ID:", plugin.id
#
#markup2 = Markup.objects.create(name="Test Markup")
#print markup2, type(markup2)
#print "markup2 ID:", markup2.id
#
#markup = Markup.objects.get(name="Test Markup")
#print markup, type(markup)
#print "markup2 ID:", markup.id
#
#internal_page = PagesInternal.objects.create(
#    name = "Test",
#    plugin = plugin, # The associated plugin
#    markup = markup,
#
#    content_html = "TEST content_html",
#    content_js = "TEST content_html",
#    content_css = "TEST content_html",
#    description = "Test description",
#)
#print internal_page