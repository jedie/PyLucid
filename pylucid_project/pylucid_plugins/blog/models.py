# -*- coding: utf-8 -*-

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django.db import models
from django.contrib import admin
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

# http://code.google.com/p/django-tagging/
import tagging
from tagging.fields import TagField

from pylucid.shortcuts import page_msg_or_warn
from pylucid.models import PageContent
from pylucid.markup.converter import apply_markup
from pylucid.system.auto_model_info import UpdateInfoBaseModel
#from PyLucid.tools.content_processors import apply_markup, fallback_markup
#from PyLucid.models import Page

class BlogEntry(UpdateInfoBaseModel):
    """
    A blog entry
    """
    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    markup = models.IntegerField(
        max_length=1, choices=PageContent.MARKUP_CHOICES,
        help_text="the used markup language for this entry",
    )
#    tags = TagField()
    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def get_absolute_url(self):
        url_title = slugify(self.headline)
        try:
            return urlresolvers.reverse('Blog-detail_view', kwargs={"id": self.pk, "title":url_title})
        except urlresolvers.NoReverseMatch:
            # FIXME: plugin urls can reverse in every situation :(
            return "#FIXME"

    def get_html(self):
        """
        returns the generate html code from the content applyed the markup.
        """
        return apply_markup(self, page_msg_or_warn)

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')

try:
    tagging.register(BlogEntry)
except tagging.AlreadyRegistered: # FIXME
    pass
