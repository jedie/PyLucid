# -*- coding: utf-8 -*-

"""
    PyLucid <-> Pygments
    ~~~~~~~~~~~~~~~~~~~~

    hightlight sourcecode

    http://pygments.org/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.template import mark_safe
from django.utils.translation import ugettext as _

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.utils.escape import escape, escape_django_tags
from pylucid_project.utils.diff import make_diff


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

def make_html(sourcecode, source_type, django_escape=False):
    code_html, lexer_name = pygmentize(sourcecode, source_type)
    code = HTML % {"lexer_name": lexer_name, "code_html": code_html}
    if django_escape:
        code = escape_django_tags(code)
    return mark_safe(code)

def no_hightlight(code):
    html = u'\n<pre><code>%s</code></pre>\n' % escape(code)
    return html

def get_formatter():
    formatter = HtmlFormatter(
        linenos=True, encoding="utf-8", style='colorful',
        outencoding="utf-8",
        cssclass=CSSCLASS,
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

    ext = source_type.lower().strip("'\" ").lstrip(".")

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


def get_pygmentize_diff(content1, content2):
    """
    returns the HTML-Diff hightlighted with Pygments
    Note: the complete content will be returned and not only the "diff-lines".
    """
    diff = make_diff(content1, content2, mode="Differ")
    diff = "\n".join(diff)

    # hightlight with Pygments
    diff_html = make_html(diff, source_type="diff", django_escape=True)

    return diff_html


def get_pygments_css(request):
    """
    Returns the EditableHtmlHeadFile path to pygments.css
    A page_msg would be created, if css not exists.
    """
    # import here, because it needs a database and other parts
    from pylucid_project.apps.pylucid.models import EditableHtmlHeadFile
    try:
        pygments_css = EditableHtmlHeadFile.on_site.get(filepath="pygments.css")
    except EditableHtmlHeadFile.DoesNotExist:
        request.page_msg("Error: No headfile with filepath 'pygments.css' found.")
    else:
        absolute_url = pygments_css.get_absolute_url(colorscheme=None)
        return absolute_url
