# -*- coding: utf-8 -*-

"""
    PyLucid utils
    ~~~~~~~~~~~~~

    Some tiny funtions:
        - without any imports from django or PyLucid

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from xml.sax.saxutils import escape as sax_escape

ENTITIES = {
    "{{" : "&#x7B;&#x7B;",
    "}}" : "&#x7D;&#x7D;",
    "{%" : "&#x7B;%",
    "%}" : "%&#x7D;",
}

def escape(txt):
    """"
    Normal sax escape, but also escape/quote the django template tags chars
    like "{" and "}" to the HTML character entity.
    """
    return sax_escape(txt, entities=ENTITIES)

def escape_django_tags(txt):
    """
    Escape only "{" and "}".
    """
    for source, dest in ENTITIES.iteritems():
        txt = txt.replace(source, dest)
    return txt