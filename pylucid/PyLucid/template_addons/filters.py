#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    some additional template filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    registered in: ./PyLucid/defaulttags/__init__.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode


def chmod_symbol(mod):
    """
    Transform a os.stat().st_mode octal value to a symbolic string.
    ignores meta infromation like SUID, SGID or the Sticky-Bit.
    e.g. 40755 -> rwxr-xr-x
    """
    trans_data = {
        u"0": u"---",
        u"1": u"--x",
        u"2": u"-w-",
        u"3": u"-wx",
        u"4": u"r--",
        u"5": u"r-x",
        u"6": u"rw-",
        u"7": u"rwx",
    }
    result = []
    try:
        mod = int(mod) # The django template engine gives always a unicode string
    except ValueError:
        return u""
    mod = mod & 0777 # strip "meta info"
    mod_string = u"%o" % mod

#    force_unicode()
    return u''.join(trans_data[num] for num in mod_string)
chmod_symbol.is_safe = True
chmod_symbol = stringfilter(chmod_symbol)

def get_oct(value):
    try:
        return oct(value)
    except:
        return value
get_oct.is_safe = False