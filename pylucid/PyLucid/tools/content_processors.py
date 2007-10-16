#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid content processors
    ~~~~~~~~~

    - apply a markup to a content
    - render a django template

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import warnings

from django.template import Template, Context
from django.conf import settings

from PyLucid.system.response import SimpleStringIO
from PyLucid.db.internal_pages import get_internal_page


# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('PyLucid.defaulttags')



def apply_markup(content, context, markup_object):
    """
    appy to the content the given markup
    The Markups names are from the _install Dump:
        ./PyLucid/db_dump_datadir/PyLucid_markup.py
    """
    page_msg = context["page_msg"]
    markup = markup_object.name

    if markup == 'textile':
        from PyLucid.system.tinyTextile import TinyTextileParser
        out_obj = SimpleStringIO()
        markup_parser = TinyTextileParser(out_obj, context)
        markup_parser.parse(content)
        return out_obj.getvalue()
    elif markup == 'Textile (original)':
        try:
            import textile
        except ImportError:
            page_msg(
                "Markup error: The Python textile library isn't installed."
                " Download: http://cheeseshop.python.org/pypi/textile"
            )
            return content
        else:
            return textile.textile(
                content,
                encoding=settings.DEFAULT_CHARSET,
                output=settings.DEFAULT_CHARSET
            )
    elif markup == 'Markdown':
        try:
            import markdown
        except ImportError:
            page_msg(
                "Markup error: The Python markdown library isn't installed."
                " Download: http://sourceforge.net/projects/python-markdown/"
            )
            return content
        else:
            return markdown.markdown(content)
    elif markup == 'ReStructuredText':
        try:
            from docutils.core import publish_parts
        except ImportError:
            page_msg(
                "Markup error: The Python docutils library isn't installed."
                " Download: http://docutils.sourceforge.net/"
            )
            return content
        else:
            docutils_settings = getattr(
                settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {}
            )
            parts = publish_parts(
                source=content, writer_name="html4css1",
                settings_overrides=docutils_settings
            )
            return parts["fragment"]
    else:
        return content


def render_string_template(content, context):
    """
    Render a template.
    """
    context2 = Context(context)
    template = Template(content)
    html = template.render(context2)
    return html


def replace_add_data(context, content):
    """
    Replace the temporary inserted "add data" tag, with all collected CSS/JS
    contents, e.g. from the internal pages.
    Note: The tag added in PyLucid.plugins_internal.page_style
    """
    try:
        internal_page = get_internal_page("page_style", "add_data")
        internal_page_content = internal_page.content_html

        context = {
            "js_data": context["js_data"],
            "css_data": context["css_data"],
        }
        html = render_string_template(internal_page_content, context)
    except Exception, msg:
        html = "<!-- Replace the ADD_DATA_TAG error: %s -->" % msg

    content = content.replace(settings.ADD_DATA_TAG, html)
    return content


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



from xml.sax.saxutils import escape as sax_escape
ENTITIES = {
#    &amp;#x7B;% lucidTag RSS url=&quot;http url&quot; title=&quot;a feed&quot; %&amp;#x7D;
    "{" : "&#x7B;",
    "}" : "&#x7D;",
}
def escape(txt):
    """"
    Normal sax escape, but also escape/quote the django template tags chars
    like "{" and "}" to the HTML character entity.
    """
    return sax_escape(txt, entities=ENTITIES)

def escape_django_tags(txt):
    """
    Escape only "{" and "}".
    """
    for source, dest in ENTITIES.iteritems():
        txt = txt.replace(source, dest)
    return txt