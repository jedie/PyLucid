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