#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid content processors
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tools around content:

    - apply a markup to a content
    - render a django template
    - redirect warnings

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import warnings

from django.conf import settings
from django.template import Template, Context
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_unicode

from PyLucid.system.response import SimpleStringIO

# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('PyLucid.template_addons')

#______________________________________________________________________________
# MARKUP

def fallback_markup(content):
    """
    A simplest markup, build only paragraphs.
    """
    import re
    content = content.replace("\r\n", "\n").replace("\r","\n")
    blocks = re.split("\n{2,}", content)
    blocks = [line.replace("\n", "<br />\n") for line in blocks]
    content = "<p>" + "</p>\n\n<p>".join(blocks) + "</p>"
    return content

def apply_tinytextile(content, context):
    """ tinyTextile markup """
    from PyLucid.system.markups.tinyTextile import TinyTextileParser
    out_obj = SimpleStringIO()
    markup_parser = TinyTextileParser(out_obj, context)
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
    from PyLucid.system.markups.creole2html import Parser, HtmlEmitter
    document = Parser(content).parse()
    return HtmlEmitter(document).emit()


def apply_markup(content, context, markup_no):
    """
    Apply to the content the given markup.
    Makrups IDs defined in
        ./PyLucid/models.py
    """
    request  = context["request"]
    page_msg = request.page_msg

    if markup_no == 2: # textile
        content = apply_tinytextile(content, context)
    elif markup_no == 3: # Textile (original)
        content = apply_textile(content, page_msg)
    elif markup_no == 4: # Markdown
        content = apply_markdown(content, page_msg)
    elif markup_no == 5: # ReStructuredText
        content = apply_restructuretext(content, page_msg)
    elif markup_no == 6: # Creole wiki markup
        content = apply_creole(content)

    return mark_safe(content) # turn djngo auto-escaping off


#______________________________________________________________________________


def render_string_template(content, context, autoescape=True):
    """
    Render a template.
    """
    context2 = Context(context, autoescape)
    template = Template(content)
    html = template.render(context2)
    return html


#______________________________________________________________________________


def redirect_warnings(out_obj):
    """
    Redirect every "warning" messages into the out_obj.
    """
#    old_showwarning = warnings.showwarning
    def showwarning(message, category, filename, lineno):
        msg = unicode(message)
        if settings.DEBUG:
            filename = u"..." + filename[-30:]
            msg += u" (%s - line %s)" % (filename, lineno)
        out_obj.write(msg)

    warnings.showwarning = showwarning



