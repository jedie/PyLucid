# coding: utf-8


"""
    PyLucid <-> Pygments
    ~~~~~~~~~~~~~~~~~~~~

    hightlight sourcecode with http://pygments.org/

    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe
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


def get_lexer(source_type, sourcecode):
    errors = []
    try:
        if source_type == "":
            return lexers.guess_lexer(sourcecode)
        else:
            return lexers.get_lexer_by_name(source_type)
    except lexers.ClassNotFound, err:
        errors.append(err)

    try: # try if given source_type is a filename
        return lexers.get_lexer_for_filename(source_type, sourcecode)
    except lexers.ClassNotFound, err:
        errors.append(err)

    try: # try if given source_type is a mimetype
        return lexers.get_lexer_for_mimetype(source_type)
    except lexers.ClassNotFound, err:
        errors.append(err)

    raise lexers.ClassNotFound(",\n ".join([str(err) for err in errors]))


def pygmentize(sourcecode, source_type):
    """
    returned html-code and the lexer_name
    """
    if not PYGMENTS_AVAILABLE:
        lexer_name = escape(source_type)
        html = no_hightlight(sourcecode)
        return html, lexer_name

    source_type = source_type.lower().strip("'\" ").lstrip(".")

    try:
        lexer = get_lexer(source_type, sourcecode)
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


