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

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import shlex
from xml.sax.saxutils import escape as sax_escape

ENTITIES = {
    "{{" : "&#x7B;&#x7B;",
    "}}" : "&#x7D;&#x7D;",
    "{%" : "&#x7B;%",
    "%}" : "%&#x7D;",
}

def escape(txt):
    """
    Escape "&", "<", ">" and django template tags chars like "{" and "}"
    defined in ENTITIES to the HTML character entity.
    >>> escape("<test1> & {{ test2 }} {% test3 %}")
    '&lt;test1&gt; &amp; &#x7B;&#x7B; test2 &#x7D;&#x7D; &#x7B;% test3 %&#x7D;'
    """
    return sax_escape(txt, entities=ENTITIES)

def escape_django_tags(txt):
    """
    Escape only django template tags chars like "{" and "}" defined in ENTITIES
    to the HTML character entity.

    >>> escape_django_tags("<test1> &")
    '<test1> &'

    >>> escape_django_tags("{{ test2 }} {% test3 %}")
    '&#x7B;&#x7B; test2 &#x7D;&#x7D; &#x7B;% test3 %&#x7D;'
    """
    for source, dest in ENTITIES.iteritems():
        txt = txt.replace(source, dest)
    return txt


# For make_kwargs()
KEYWORD_MAP = {
    "True": True,
    "False": False,
    "None": None,
}

def make_kwargs(raw_content, encoding="UTF-8"):
    """
    convert a string into a dictionary. e.g.:

    >>> make_kwargs('key1="value1" key2="value2"')
    {'key2': 'value2', 'key1': 'value1'}

    >>> make_kwargs('A="B" C=1 D=1.1 E=True F=False G=None')
    {'A': 'B', 'C': 1, 'E': True, 'D': '1.1', 'G': None, 'F': False}
    
    >>> make_kwargs('''key1="'1'" key2='"2"' key3="""'3'""" ''')
    {'key3': 3, 'key2': 2, 'key1': 1}

    >>> make_kwargs(u'unicode=True')
    {'unicode': True}
    """
    if isinstance(raw_content, unicode):
        # shlex.split doesn't work with unicode?!?
        raw_content = raw_content.encode(encoding)

    parts = shlex.split(raw_content)

    result = {}
    for part in parts:
        key, value = part.split("=", 1)

        if value in KEYWORD_MAP:
            # True False or None
            value = KEYWORD_MAP[value]
        else:
            # A number?
            try:
                value = int(value.strip("'\""))
            except ValueError:
                pass

        result[key] = value

    return result



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."