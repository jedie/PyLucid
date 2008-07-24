# -*- coding: utf-8 -*-

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from PyLucid.tools.content_processors import apply_markup, fallback_markup
from PyLucid.models.Page import MARKUPS


class BlogComment(models.Model):
    """
    comment from non-registered users
    """
    blog_entry = models.ForeignKey("BlogEntry")

    ip_address = models.IPAddressField(_('ip address'),)
    person_name = models.CharField(
        _("person's name"), max_length=50,
        help_text=_("Your full name (will be published) (required)"),
    )
    email = models.EmailField(
        _('e-mail address'),
        help_text=_("Only for internal use. (will not be published) (required)"),
    )
    homepage = models.URLField(
        _("homepage"), help_text = _("Your homepage (optional)"),
        verify_exists = False, max_length = 200,
        null=True, blank=True
    )

    content = models.TextField(_('content'), max_length=3000)

    is_public = models.BooleanField(_('is public'))

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False,
        help_text="User how create the current comment.",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(
        User, editable=False,
        help_text="User as last edit the current comment.",
        null=True, blank=True
    )

    def html_content(self):
        """
        returns the content as html used a simple markup.
        """
        safe_content = strip_tags(self.content)
        content = fallback_markup(safe_content)
        return mark_safe(content)

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('createtime', 'lastupdatetime')

#______________________________________________________________________________


class BlogTagManager(models.Manager):
    """
    Manager for BlogTag model.
    """
    def get_or_creates(self, tags_string):
        """
        split the given tags_string and create not existing tags.
        returns a list of all tag model objects and a list of all created tags.
        """
        tag_objects = []
        new_tags = []
        for tag_name in tags_string.split(" "):
            tag_name = tag_name.strip().lower()
            try:
                tag_obj = self.get(name = tag_name)
            except self.model.DoesNotExist:
                new_tags.append(tag_name)
                tag_obj = self.create(name = tag_name, slug = tag_name)

            tag_objects.append(tag_obj)

        return tag_objects, new_tags


class BlogTag(models.Model):
    """
    A blog entry tag
    """
    objects = BlogTagManager()

    name = models.CharField(max_length=255, core=True, unique=True)
    slug = models.SlugField(
        unique=True, prepopulate_from=('tag',), max_length=120
    )

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('name',)

#______________________________________________________________________________

class BlogEntry(models.Model):
    """
    A blog entry
    """
    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    markup = models.IntegerField(
        max_length=1, choices=MARKUPS,
        help_text="the used markup language for this entry",
    )

    tags = models.ManyToManyField(BlogTag, blank=True)

    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User,
        editable = False,
    )
    lastupdateby = models.ForeignKey(
        User,
        editable = False,
        null=True, blank=True
    )

    def html_content(self, context):
        """
        returns the generatet html code from the content applyed the markup.
        """
        return apply_markup(
            content = self.content,
            context = context,
            markup_no = self.markup
        )

    def get_tag_string(self):
        """
        Returns all tags as a joined string
        """
        tags = self.tags.all()
        tags_names = [i.name for i in tags]
        return " ".join(tags_names)

    def __unicode__(self):
        return self.headline

    class Admin:
        pass

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('-createtime', '-lastupdatetime')