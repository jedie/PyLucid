
from PyLucid.tools.content_processors import escape

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

def make_html(sourcecode, source_type):
    code_html, lexer_name = pygmentize(sourcecode, source_type)
    code = HTML % {"lexer_name": lexer_name, "code_html": code_html}
    return code

def no_hightlight(code):
    html = '\n<pre><code>%s</code></pre>\n' % escape(code)
    return html


def pygmentize(sourcecode, source_type):
    """
    returned html-code and the lexer_name
    """
    if not pygments_available:
        lexer_name = escape(source_type)
        html = no_hightlight(sourcecode)
        return html, lexer_name

    ext = source_type.lower().lstrip(".")

    try:
        lexer = lexers.get_lexer_by_name(ext)
    except lexers.ClassNotFound, err:
        lexer_name = "[Hightlight Error: %s]<br />\n" % err
        html = no_hightlight(sourcecode)
        return html, lexer_name


    lexer_name = lexer.name

    formatter = HtmlFormatter(
        linenos=True, encoding="utf-8", style='colorful'
    )

    stylesheet = formatter.get_style_defs('.pygments_code')

#    self.context["css_data"].append({
#        "from_info": "tinyTextile",
#        "data": stylesheet,
#    })

    out_object = SimpleStringIO()
    highlight(sourcecode, lexer, formatter, out_object)
    html = out_object.getvalue()

    return html, lexer_name

