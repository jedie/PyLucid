# -*- coding: utf-8 -*-

"""
    PyLucid escape
    ~~~~~~~~~~~~~~
    
    * Escape "&", "<", ">" and django template tags chars like "{" and "}"
    * Escape only django template tags chars like "{" and "}"

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
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


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."