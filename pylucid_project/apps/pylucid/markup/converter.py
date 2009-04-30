# -*- coding: utf-8 -*-

"""
    PyLucid markup converter
    ~~~~~~~~~~~~~~~~~~~~~~~~

    apply a markup to a content

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import re

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"

from django.conf import settings
#from django.template import Template, Context
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_unicode

from pylucid.markup.django_tags import DjangoTagAssembler
from pylucid_project.utils.SimpleStringIO import SimpleStringIO

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
    content = content.replace("\r\n", "\n").replace("\r","\n")
    blocks = BLOCK_RE.split(content)
    blocks = [line.replace("\n", "<br />\n") for line in blocks]
    content = "<p>" + "</p>\n\n<p>".join(blocks) + "</p>"
    content = LINK_RE.sub(r'<a href="\g<url>">\g<title></a>', content)
    return content

def apply_tinytextile(content, page_msg):
    """ tinyTextile markup """
    from pylucid.markup.tinyTextile import TinyTextileParser
    out_obj = SimpleStringIO()
    markup_parser = TinyTextileParser(out_obj, page_msg)
    markup_parser.parse(content)
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
        return force_unicode(textile.textile(
            smart_str(content),
            encoding=settings.DEFAULT_CHARSET,
            output=settings.DEFAULT_CHARSET
        ))

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
        if getattr(markdown, "version_info", None) < (1,7):
            return force_unicode(markdown.markdown(smart_str(content)))
        else:
            return markdown.markdown(content)


def apply_restructuretext(content, page_msg):
    try:
        from docutils.core import publish_parts
    except ImportError:
        page_msg(
            "Markup error: The Python docutils library isn't installed."
            " Download: http://docutils.sourceforge.net/"
        )
        return fallback_markup(content)
    else:
        docutils_settings = getattr(
            settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {}
        )
        parts = publish_parts(
            source=content, writer_name="html4css1",
            settings_overrides=docutils_settings
        )
        return parts["fragment"]



def apply_creole(content):
    """
    Use python-creole:
    http://code.google.com/p/python-creole/
    
    We used verbose=1 for inser error information (e.g. not existing macro)
    into the generated page
    """
    from pylucid.markup import PyLucid_creole_macros
    
    from creole import Parser
    from creole.creole2html import HtmlEmitter
   
    # Create document tree from creole markup
    document = Parser(content).parse()
    
    # Build html code from document tree
    return HtmlEmitter(document, macros=PyLucid_creole_macros, verbose=0).emit()



def apply_markup(pagecontent, page_msg):
    """
    Apply to the content the given markup.
    Makrups IDs defined in
        ./PyLucid/models.py
    """
    markup_no = pagecontent.markup
    raw_content = pagecontent.content
    
    assemble_tags = markup_no not in (pagecontent.MARKUP_HTML, pagecontent.MARKUP_HTML_EDITOR)
    if assemble_tags:
        # cut out every django tags from content
        assembler = DjangoTagAssembler()
        raw_content2, cut_data = assembler.cut_out(raw_content)
    
    if markup_no == pagecontent.MARKUP_TINYTEXTILE: # PyLucid's TinyTextile
        html_content = apply_tinytextile(raw_content2, page_msg)
        
    elif markup_no == pagecontent.MARKUP_TEXTILE: # Textile (original)
        html_content = apply_textile(raw_content2, page_msg)
        
    elif markup_no == pagecontent.MARKUP_MARKDOWN:
        html_content = apply_markdown(raw_content2, page_msg)
        
    elif markup_no == pagecontent.MARKUP_REST:
        html_content = apply_restructuretext(raw_content2, page_msg)
        
    elif markup_no == pagecontent.MARKUP_CREOLE:
        html_content = apply_creole(raw_content2)

    if assemble_tags:
        # reassembly cut out django tags into text
        html_content2 = assembler.reassembly(html_content, cut_data)
    else:
        # html "markup" used
        html_content2 = raw_content

    return mark_safe(html_content2) # turn djngo auto-escaping off



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
