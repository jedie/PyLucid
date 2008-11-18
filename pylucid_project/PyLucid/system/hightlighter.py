# -*- coding: utf-8 -*-

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

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from PyLucid.tools.utils import escape, escape_django_tags

from django.utils.translation import ugettext as _
from django.conf import settings

from PyLucid.system.response import SimpleStringIO

try:
    import pygments
    from pygments import lexers
    from pygments.formatters import HtmlFormatter
    from pygments import highlight
    PYGMENTS_AVAILABLE = True
except ImportError, err:
    PYGMENTS_AVAILABLE = False
    import_error = err

HTML = (
    u'<fieldset class="pygments_code">\n'
    '<legend class="pygments_code">%(lexer_name)s</legend>'
    '%(code_html)s'
    '</fieldset>\n'
)
# There exist a bug in pygments, if cssclass is given as unicode:
# http://dev.pocoo.org/projects/pygments/ticket/371
CSSCLASS = "pygments"

def make_html(sourcecode, source_type):
    code_html, lexer_name = pygmentize(sourcecode, source_type)
    code = HTML % {"lexer_name": lexer_name, "code_html": code_html}
    return code

def no_hightlight(code):
    html = u'\n<pre><code>%s</code></pre>\n' % escape(code)
    return html

def get_formatter():
    formatter = HtmlFormatter(
        linenos=True, encoding="utf-8", style='colorful',
        outencoding = "utf-8",
        cssclass = CSSCLASS,
    )
    return formatter

def pygmentize(sourcecode, source_type):
    """
    returned html-code and the lexer_name
    """
    if not PYGMENTS_AVAILABLE:
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
        lexer_name = u'<small title="%s">%s</small>' % (err, info)
        html = no_hightlight(sourcecode)
        return html, lexer_name

    lexer_name = lexer.name

    formatter = get_formatter()

    out_object = SimpleStringIO()
    try:
        highlight(sourcecode, lexer, formatter, out_object)
    except Exception, err:
        if settings.DEBUG:
            raise
        html = no_hightlight(sourcecode)
        lexer_name += " (Error: %s)" % err
    else:
        html = out_object.getvalue()

        # If there is e.g. html code with django tags, we must escape this:
        html = escape_django_tags(html)
        html = html.decode("utf-8")

    return html, lexer_name


