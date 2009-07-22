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
from django.core import urlresolvers
from django.db.models import signals
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

# http://code.google.com/p/django-tagging/
import tagging
from tagging.fields import TagField

from pylucid_plugins import page_update_list

from pylucid.shortcuts import page_msg_or_warn
from pylucid.models import PageContent, Language
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
    lang = models.ForeignKey(Language)
    markup = models.IntegerField(
        max_length=1, choices=PageContent.MARKUP_CHOICES,
        help_text="the used markup language for this entry",
    )
#    tags = TagField()
    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def get_update_info(self):
        """ update info for page_update_list.models.UpdateJournal used by page_update_list.save_receiver """
        if not self.is_public: # Don't list non public articles
            return

        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "lang": self.lang,
            "object_url": self.get_absolute_url(),
            "title": self.headline,
        }

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


signals.post_save.connect(receiver=page_update_list.save_receiver, sender=BlogEntry)


try:
    tagging.register(BlogEntry)
except tagging.AlreadyRegistered: # FIXME
    pass
