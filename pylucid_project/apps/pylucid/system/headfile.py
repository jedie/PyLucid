# coding: utf-8

"""
    PyLucid headfile
    ~~~~~~~~~~~~~~~~

    Stores the information about CSS/JS links or content for html head.

    Used in pylucid.models and pylucid_plugins.head_files.context_middleware 

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import mimetypes
from xml.sax.saxutils import escape

from django.conf import settings
from django.utils import safestring
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


TYPE_CSS = "css"
TYPE_JS = "js"
KNOWN_TYPES = (TYPE_CSS, TYPE_JS)

DEFAULT_INLINE_ATTRIBUTES = {
    TYPE_CSS:{"type":"text/css"},
    TYPE_JS: {"type":"text/javascript"},
}
DEFAULT_LINK_ATTRIBUTES = {
    TYPE_CSS:{"type":"text/css", "rel":"stylesheet"},
    TYPE_JS: {"type":"text/javascript"},
}


class HeadfileBase(object):
    def check_type(self):
        if self.data_type not in KNOWN_TYPES:
            raise RuntimeError("Data type %r unknown!" % self.data_type)

    def get_head_tag(self):
        return render_to_string(self.template_name, self.context)



class HeadfileInline(HeadfileBase):
    """ CSS/JS content in the html head """
    def __init__(self, data_type, content, tag_attrs={}):
        self.data_type = data_type
        self.check_type()
        
        self.content = content
        
        self.tag_attrs = DEFAULT_INLINE_ATTRIBUTES[data_type]
        self.tag_attrs.update(tag_attrs)
        
        self.template_name = settings.PYLUCID.HEADFILE_INLINE_TEMPLATES % self.data_type
        self.context = {"tag_attrs": self.tag_attrs, "content": self.content,}


class HeadfileLink(HeadfileBase):
    """
    Links to CSS/JS files in html head
    TODO: Should check if the file was saved into media path
    """
    def __init__(self, url, tag_attrs={}):
        self.url = url
        if "?" in url:
            path = url.split("?",1)[0]
        else:
            path = url
        self.data_type = os.path.splitext(path)[1].lstrip(".")
        self.check_type()

        self.tag_attrs = self.make_tag_attrs(tag_attrs)
        
        self.template_name = settings.PYLUCID.HEADFILE_LINK_TEMPLATES % self.data_type      
        self.context = {"url": self.url, "tag_attrs": self.tag_attrs}
        
    def make_tag_attrs(self, tag_attrs):
        attributes = DEFAULT_LINK_ATTRIBUTES[self.data_type]
        
        if settings.DEBUG:
            attributes["onerror"] = safestring.mark_safe(
                "JavaScript:alert('Error loading file [%s] !');" % escape(self.url)
            )
        
        attributes.update(tag_attrs)
        return attributes

