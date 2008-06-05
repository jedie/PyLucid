# -*- coding: utf-8 -*-

"""
    PyLucid.tools.shortcuts
    ~~~~~~~~~~~~~~~~~~~~~~~

    Some usefull routines around `PyLucid.models.Page.shortcut`.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import string

ALLOW_CHARS = string.ascii_letters + string.digits + "_"

def verify_shortcut(shortcut):
    """
    Check a shortcut. Raise AssertionError if something seems to be wrong.
    But normaly the urls-re should only filter the bad thing from urls ;)
    """
    if shortcut=="":
        raise AssertionError("Shortcut is empty!")

    for char in shortcut:
        if not char in ALLOW_CHARS+"-":
            raise AssertionError(
                "Not allowed character in shortcut: '%r'" % char
            )

def makeUnique(item_name, name_list):
    """
    returns a URL safe, unique shortcut.
    - delete all non-ALLOW_CHARS characters.
    - if the shotcut already exists in name_list -> add a sequential number
    Note:
    Not only used for making page shortcuts unique with getUniqueShortcut(),
    also used in:
        -PyLucid.defaulttags.lucidTag.lucidTagNode._add_unique_div()
        -PyLucid.middlewares.headline_anchor.HeadlineAnchor()
    """
    # delete all non-ALLOW_CHARS characters and separate in parts
    parts = [""]
    for char in item_name:
        if not char in ALLOW_CHARS:
            if parts[-1] != "":
                # No double "-" e.g.: "foo - bar" -> "foo-bar" not "foo---bar"
                parts.append("")
        else:
            parts[-1] += char

    item_name = "-".join(parts)
    item_name = item_name.strip("-")

    if item_name == "":
        # No shortcut? That won't work.
        item_name = "1"

    name_list2 = [i.lower() for i in name_list]

    # make double shortcut unique (add a new free sequential number)
    if item_name.lower() in name_list2:
        for i in xrange(1, 1000):
            testname = "%s%i" % (item_name, i)
            if testname.lower() not in name_list2:
                item_name = testname
                break

    return item_name


def getUniqueShortcut(shortcut, exclude_shortcut=None):
    from PyLucid.models import Page

#    print "source shortcut:", shortcut
    shortcuts = Page.objects.values("shortcut")
#    print "exclude shortcut: '%s'" % exclude_shortcut
    if exclude_shortcut != None:
        shortcuts = shortcuts.exclude(shortcut=exclude_shortcut)
    existing_shortcuts = [i["shortcut"] for i in shortcuts]
#    print "existing_shortcuts:", existing_shortcuts
    return makeUnique(shortcut, existing_shortcuts)



if __name__ == "__main__":
    #
    # There exist a unitest for the page shortcuts:
    #     ./unittests/unittest_UniqueShortcuts
    #
    name_list = ["GibtsSchon", "UndAuchDas", "UndAuchDas1", "UndAuchDas2"]
    print name_list
    print "-"*80
    print makeUnique("Ich bin neu!", name_list)
    print makeUnique("gibts schon", name_list)
    print makeUnique("#und!auch(das)", name_list)
    print makeUnique("foo - bar", name_list)

    new_entry = makeUnique("Gibtsschon", name_list)
    name_list.append(new_entry)
    print new_entry

    new_entry = makeUnique("Gibtsschon", name_list)
    name_list.append(new_entry)
    print new_entry

    new_entry = makeUnique("GibtsSchon", name_list)
    name_list.append(new_entry)
    print new_entry

    new_entry = makeUnique("GibtsSchon", name_list)
    name_list.append(new_entry)
    print new_entry
