# -*- coding: utf-8 -*-

"""
    Slug
    ~~~~
    
    A slug is a short label for something, containing only letters, numbers, underscores or hyphens.
    They’re generally used in URLs. See also: http://docs.djangoproject.com/en/dev/glossary/

    Some usefull routines around unique slug.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import string

ALLOW_CHARS = string.ascii_letters + string.digits + "_"
SEPERATOR = "-"

def verify_slug(slug):
    """
    Check a slug. Raise AssertionError if something seems to be wrong.
    But normaly the urls-re should only filter the bad thing from urls ;)
    
    >>> verify_slug("ThisIs-A-Slug_123")
    
    >>> verify_slug("")
    Traceback (most recent call last):
    ...
    AssertionError: Slug is empty!
    
    >>> verify_slug("Wrong!")
    Traceback (most recent call last):
    ...
    AssertionError: Not allowed character in slug: '!'
    """
    if slug=="":
        raise AssertionError("Slug is empty!")

    for char in slug:
        if not char in ALLOW_CHARS+SEPERATOR:
            raise AssertionError(
                "Not allowed character in slug: %r" % char
            )


def makeUniqueSlug(item_name, existing_slugs=[]):
    """
    returns a URL safe, unique slug.
    - delete all non-ALLOW_CHARS characters.
    - if the shotcut already exists in existing_slugs -> add a sequential number
    Note:
    Not only used for making page slugs unique with getUniqueSlug(),
    also used in:
        -PyLucid.defaulttags.lucidTag.lucidTagNode._add_unique_div()
        -PyLucid.middlewares.headline_anchor.HeadlineAnchor()
    
    >>> makeUniqueSlug("Please make *me* slug!")
    'Please-make-me-slug'
    >>> makeUniqueSlug("And me - too! -, please.")
    'And-me-too-please'
    
    >>> existing_slugs = ["Exist", "ExistToo", "ExistToo1"]
    >>> makeUniqueSlug("NewItem", existing_slugs)
    'NewItem'
    >>> makeUniqueSlug("Exist", existing_slugs)
    'Exist1'
    >>> makeUniqueSlug("ExistToo", existing_slugs)
    'ExistToo2'
    
    to make a slug unique we ignore case!
    >>> makeUniqueSlug("SLUG", existing_slugs=['slug',"Slug1"])
    'SLUG2'
    
    If item is empty, we get '1' back:
    >>> makeUniqueSlug("", [])
    '1'
    """
    # delete all non-ALLOW_CHARS characters and separate in parts
    parts = [""]
    for char in item_name:
        if not char in ALLOW_CHARS:
            if parts[-1] not in ("", SEPERATOR):
                # No double "-" e.g.: "foo - bar" -> "foo-bar" not "foo---bar"
                parts.append("")
        else:
            parts[-1] += char

    item_name = SEPERATOR.join(parts)
    item_name = item_name.strip(SEPERATOR)

    if item_name == "":
        # No slug? That won't work.
        item_name = "1"
        
    if existing_slugs==[]:
        return item_name

    existing_slugs2 = [i.lower() for i in existing_slugs]

    # make double slug unique (add a new free sequential number)
    if item_name.lower() in existing_slugs2:
        for i in xrange(1, 1000):
            testname = "%s%i" % (item_name, i)
            if testname.lower() not in existing_slugs2:
                item_name = testname
                break

    return item_name


#def getUniqueSlug(slug, exclude_slug=None):
#    from PyLucid.models import Page
#
##    print "source slug:", slug
#    slugs = Page.objects.values("slug")
##    print "exclude slug: '%s'" % exclude_slug
#    if exclude_slug != None:
#        slugs = slugs.exclude(slug=exclude_slug)
#    existing_slugs = [i["slug"] for i in slugs]
##    print "existing_slugs:", existing_slugs
#    return makeUniqueSlug(slug, existing_slugs)



if __name__ == "__main__":
    #
    # There exist a unitest for the page slugs:
    #     ./unittests/unittest_UniqueSlugs
    #
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
