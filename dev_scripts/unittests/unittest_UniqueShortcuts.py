#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local page shortcut test with a full init PyLucid environment.
"""

from setup_environment import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True
)

#______________________________________________________________________________
# Test:

from PyLucid.models import Page, Preference

auto_shortcuts = Preference.objects.get(name='auto shortcuts')
print "auto_shortcuts:", auto_shortcuts.value
auto_shortcuts.value = False
auto_shortcuts.save()
auto_shortcuts = Preference.objects.get(name='auto shortcuts').value
print "auto_shortcuts:", auto_shortcuts


def verbose_save(page, new_shortcut):
    print "source......: '%s'" % page.shortcut
    print "new shortcut: '%s'" % new_shortcut
    page.shortcut = new_shortcut
    page.save()
    print "after save..: '%s'" % page.shortcut

# get the first page
page = Page.objects.all()[0]

print
print "change the source sortcut"
new_shortcut = "A_New_ShortCut"
verbose_save(page, new_shortcut)
assert page.shortcut == new_shortcut


print
print "Test the non-ASCII string"
verbose_save(page, "--=[Short cut test]=--")
assert page.shortcut == "Short-cut-test"

print
print "Test the non-ASCII string 2"
verbose_save(page, "Short cut - test")
assert page.shortcut == "Short-cut-test"

print
print "No empty shortcut allowed"
verbose_save(page, "")
assert page.shortcut != ""


print
print "Unique Test"
test = "UniqueShortCutTest"
verbose_save(page, test)
page2 = Page.objects.all()[1] # Get the second page
verbose_save(page2, test)
assert page.shortcut != page2.shortcut
assert page2.shortcut == "UniqueShortCutTest1"

print
print "update a page only. (Shourtcut should not be changed!)"
verbose_save(page, test)
assert page.shortcut == "UniqueShortCutTest"
verbose_save(page, test)
assert page.shortcut == "UniqueShortCutTest"

print
print "insert a new page with a existing shortcut"
# For page.id = None look at:
# http://www.djangoproject.com/documentation/db-api/#how-django-knows-to-update-vs-insert
page.id = None # django means the side would be new.
verbose_save(page, test)
assert page.shortcut == "UniqueShortCutTest2"

page.id = None # django means the side would be new.
verbose_save(page, test)
assert page.shortcut == "UniqueShortCutTest3"
