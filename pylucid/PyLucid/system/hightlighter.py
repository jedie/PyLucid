#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid <-> Pygments
    ~~~~~~~~~~~~~~~~~~~~

    hightlight sourcecode

    http://pygments.org/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from PyLucid.tools.content_processors import escape, escape_django_tags

from django.utils.translation import ugettext as _
from django.conf import settings

from PyLucid.system.response import SimpleStringIO

try:
    from pygments import lexers
    from pygments.formatters import HtmlFormatter
    from pygments import highlight
    pygments_available = True
except ImportError:
    pygments_available = False

HTML = (
    '<fieldset class="pygments_code">'
    '<legend class="pygments_code">%(lexer_name)s</legend>'
    '%(code_html)s'
    '</fieldset>'
)
CSSCLASS = "pygments"

def make_html(sourcecode, source_type):
    code_html, lexer_name = pygmentize(sourcecode, source_type)
    code = HTML % {"lexer_name": lexer_name, "code_html": code_html}
    return code

def no_hightlight(code):
    html = '\n<pre><code>%s</code></pre>\n' % escape(code)
    return html

def get_formatter():
    formatter = HtmlFormatter(
        linenos=True, encoding="utf-8", style='colorful',
        cssclass = CSSCLASS,
    )
    return formatter

def pygmentize(sourcecode, source_type):
    """
    returned html-code and the lexer_name
    """
    if not pygments_available:
        lexer_name = escape(source_type)
        html = no_hightlight(sourcecode)
        return html, lexer_name

    ext = source_type.lower().lstrip(".").strip("'\"")

    try:
        if ext == "":
            lexer = lexers.guess_lexer(sourcecode)
        else:
            lexer = lexers.get_lexer_by_name(ext)
    except lexers.ClassNotFound, err:
        info = _("unknown type")
        lexer_name = '<small title="%s">%s</small>' % (err, info)
        html = no_hightlight(sourcecode)
        return html, lexer_name

    lexer_name = lexer.name

    formatter = get_formatter()

    out_object = SimpleStringIO()
    highlight(sourcecode, lexer, formatter, out_object)
    html = out_object.getvalue()

    # If there is e.g. html code with django tags, we must escape this:
    html = escape_django_tags(html)

    return html, lexer_name


