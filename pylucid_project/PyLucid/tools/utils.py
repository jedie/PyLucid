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

import shlex, re
from xml.sax.saxutils import escape as sax_escape

from django.utils.safestring import mark_safe


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
    txt = sax_escape(txt, entities=ENTITIES)
    return mark_safe(txt) 

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




def contains_char(text, chars):
    """
    returns True if text contains a characters from the given chars list.
    
    >>> contains_char("1234", ["a", "b"])
    False
    >>> contains_char("1234", ["2", "b"])
    True
    >>> contains_char("1234", "wrong")
    Traceback (most recent call last):
    ...
    AssertionError
    """
    assert isinstance(chars, (list, tuple))
    for char in chars:
        if char in text:
            return True
    return False




def cutout(content, terms, max_lines=5, cutout_len=10):
    """
    Cut out all lines witch contains one of the terms.
    
    The >cutout_len< argument sets the size of the text around the match:
    
    >>> cutout("1234567890", ["3", "8"], cutout_len=2)
    [('12', '3', '45'), ('67', '8', '90')]
    >>> cutout("1234567890", ["1", "0"], cutout_len=3)
    [('', '1', '234'), ('789', '0', '')]
    
    
    The >max_lines< argument is the maximum cutouts for all terms:
    
    >>> cutout("1x1 2y2 3x3 4y4", ["x", "y"], max_lines=1, cutout_len=1)
    [('1', 'x', '1')]
    >>> cutout("1x1 2y2 3x3 4y4", ["x", "y"], max_lines=2, cutout_len=1)
    [('1', 'x', '1'), ('2', 'y', '2')]
    >>> cutout("1x1 2y2 3x3 4y4", ["x", "y"], max_lines=3, cutout_len=1)
    [('1', 'x', '1'), ('2', 'y', '2'), ('3', 'x', '3')]
    """
    re_terms = [re.escape(term) for term in terms]
    regex = re.compile(
        r"(.{0,%(cutout)i})(%(terms)s)(.{0,%(cutout)i})" % {
            "cutout": cutout_len,
            "terms": "|".join(re_terms)
        },
        re.DOTALL | re.IGNORECASE
    )

    result = []
    for no, m in enumerate(regex.finditer(content)):#, start=1):
        result.append(m.groups())
        if no+1 >= max_lines: # enumerate start argument it new in Python 2.6
            break

    return result





if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."