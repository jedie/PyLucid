# coding: utf-8

"""
    utils
    ~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import unicodedata


def clean_string(value):
    """
    >>> clean_string("test")
    'test'
    >>> clean_string("s p a c e s")
    's_p_a_c_e_s'
    >>> clean_string("German Umlaute are ä,ö,ü and ß")
    'German_Umlaute_are_a_o_u_and'
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s]', ' ', value).strip()
    return re.sub('[_\s]+', '_', value)


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration("type error")
    Traceback (most recent call last):
        ...
    TypeError: human_duration() argument must be integer or float

    >>> human_duration(0.01)
    u'10.0 ms'
    >>> human_duration(0.9)
    u'900.0 ms'
    >>> human_duration(65.5)
    u'1.1 min'
    >>> human_duration((60 * 60)-1)
    u'59.0 min'
    >>> human_duration(60*60)
    u'1.0 hours'
    >>> human_duration(1.05*60*60)
    u'1.1 hours'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    u'2.5 years'
    """
    if not isinstance(t, (int, float)):
        raise TypeError("human_duration() argument must be integer or float")

    chunks = (
      (60 * 60 * 24 * 365, u'years'),
      (60 * 60 * 24 * 30, u'months'),
      (60 * 60 * 24 * 7, u'weeks'),
      (60 * 60 * 24, u'days'),
      (60 * 60, u'hours'),
    )

    if t < 1:
        return u"%.1f ms" % round(t * 1000, 1)
    if t < 60:
        return u"%.1f sec" % round(t, 1)
    if t < 60 * 60:
        return u"%.1f min" % round(t / 60, 1)

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return u"%(number).1f %(type)s" % {'number': count, 'type': name}