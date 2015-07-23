# coding: utf-8

"""
    PyLucid markup converter
    ~~~~~~~~~~~~~~~~~~~~~~~~

    apply a markup to a content

    :copyleft: 2007-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import re
import io
import sys

from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_text

from django_tools.utils.messages import FileLikeMessages

from pylucid_migration.markup import MARKUP_TINYTEXTILE, \
    MARKUP_TEXTILE, MARKUP_MARKDOWN, MARKUP_REST, MARKUP_CREOLE, MARKUP_HTML, \
    MARKUP_HTML_EDITOR, MARKUP_DICT
from pylucid_migration.markup.django_tags import DjangoTagAssembler, PartText
#from pylucid_project.utils.escape import escape_django_tags as escape_django_template_tags

from pylucid_migration.markup.django_tags import PartDjangoTag, PartBlockTag, PartLucidTag

#______________________________________________________________________________
# MARKUP

BLOCK_RE = re.compile("\n{2,}")

LINK_RE = re.compile(
    r'''(?<!=")(?P<url>(http|ftp|svn|irc)://(?P<title>[^\s\<]+))(?uimx)'''
)

def fallback_markup(content):
    """
    A simplest markup, build only paragraphs.
    >>> fallback_markup("line one\\nline two\\n\\nnext block")
    '<p>line one<br />\\nline two</p>\\n\\n<p>next block</p>'

    >>> fallback_markup("url: http://pylucid.org END")
    '<p>url: <a href="http://pylucid.org">pylucid.org</a> END</p>'
    """
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = BLOCK_RE.split(content)
    blocks = [line.replace("\n", "<br />\n") for line in blocks]
    content = "<p>" + "</p>\n\n<p>".join(blocks) + "</p>"
    content = LINK_RE.sub(r'<a href="\g<url>">\g<title></a>', content)
    return content

def apply_tinytextile(content, page_msg):
    """ tinyTextile markup """
    from pylucid_migration.markup.tinyTextile import TinyTextileParser
    out_obj = io.StringIO()
    markup_parser = TinyTextileParser(out_obj, page_msg)
    markup_parser.parse(smart_str(content))
    return out_obj.getvalue()


def apply_textile(content, page_msg):
    """ Original textile markup """
    try:
        import textile
    except ImportError:
        page_msg(
            "Markup error: The Python textile library isn't installed."
            " Download: http://cheeseshop.python.org/pypi/textile"
        )
        return fallback_markup(content)
    else:
        return textile.textile(
            smart_str(content),
            encoding=settings.DEFAULT_CHARSET,
            output=settings.DEFAULT_CHARSET
        )

def apply_markdown(content, page_msg):
    """ Markdown markup """
    try:
        import markdown
    except ImportError:
        page_msg(
            "Markup error: The Python markdown library isn't installed."
            " Download: http://sourceforge.net/projects/python-markdown/"
        )
        return fallback_markup(content)
    else:
        # unicode support only in markdown v1.7 or above.
        # version_info exist only in markdown v1.6.2rc-2 or above.
        if getattr(markdown, "version_info", None) < (1, 7):
            return force_text(markdown.markdown(smart_str(content)))
        else:
            return markdown.markdown(content)


def apply_restructuretext(content, page_msg):
    from creole.exceptions import DocutilsImportError
    try:
        from creole.rest_tools.clean_writer import rest2html
    except DocutilsImportError:
        page_msg(
            "Markup error: The Python docutils library isn't installed."
            " Download: http://docutils.sourceforge.net/"
        )
        return fallback_markup(content)
    else:
        #docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
        rest = rest2html(content)
        return rest


def apply_creole(content, verbose = 2):
    """
    Use python-creole:
    http://code.google.com/p/python-creole/

    We used verbose for insert error information (e.g. not existing macro)
    into the generated page
    """
    from creole import creole2html
    from pylucid_migration.markup import PyLucid_creole_macros

    # new python-creole v1.0 API
    return creole2html(content,
        macros=PyLucid_creole_macros,
        stderr=sys.stderr, #verbose=verbose
    )


def convert(raw_content, markup_no):
    page_msg=sys.stderr.write # XXX
    if markup_no == MARKUP_TINYTEXTILE: # PyLucid's TinyTextile
        html_content = apply_tinytextile(raw_content, page_msg)
    elif markup_no == MARKUP_TEXTILE: # Textile (original)
        html_content = apply_textile(raw_content, page_msg)
    elif markup_no == MARKUP_MARKDOWN:
        html_content = apply_markdown(raw_content, page_msg)
    elif markup_no == MARKUP_REST:
        html_content = apply_restructuretext(raw_content, page_msg)
    elif markup_no == MARKUP_CREOLE:
        html_content = apply_creole(raw_content, page_msg)
    elif markup_no in (MARKUP_HTML, MARKUP_HTML_EDITOR):
        html_content = raw_content
    else:
        raise AssertionError("markup no %r unknown!" % markup_no)

    return html_content


def apply_markup(raw_content, markup_no):
    """ render markup content to splitted parts list """

    assembler = DjangoTagAssembler()
    raw_content2 = assembler.cut_out(raw_content, escape=True)

    html_content = convert(raw_content2, markup_no)

    # Cutout again: e.g.: for creole <<code>>..<</code>> markup
    html_content2 = assembler.cut_out(html_content, escape=False)

    return assembler.reassembly_splitted(html_content2)

def markup2html(raw_content, markup_no):
    splitted_content = apply_markup(raw_content, markup_no)
    html=""
    for part in splitted_content:
        # print(part)
        if isinstance(part, PartBlockTag):
            html+=part.get_html()
        else:
            content = part.content
            html+=content
    return html, splitted_content


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print("DocTest end.")
