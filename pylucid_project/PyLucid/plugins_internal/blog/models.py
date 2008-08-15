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
from django.contrib import admin
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

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

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('createtime', 'lastupdatetime')

class BlogCommentAdmin(admin.ModelAdmin):
    pass

try:
    admin.site.register(BlogComment, BlogCommentAdmin)
except admin.sites.AlreadyRegistered:
    pass # FIXME

#______________________________________________________________________________


BAD_TAG_SLUG_CHARS = (" ", "/", ";")
class BlogTagManager(models.Manager):
    """
    Manager for BlogTag model.
    """
    def safe_get(self, slug):
        """
        Get a tag entry by slug. Try to verify the slug before we access the
        database. Should be used, if the slug comes from the Client
        (e.g. via url)
        TODO: Exist there a better way to verify the tag slug?
        """
        slug = slug.strip("/") # If it comes from url args
        for char in BAD_TAG_SLUG_CHARS:
            if char in slug:
                raise self.model.DoesNotExist("Not allowed character in tag name!")

        return self.model.objects.get(slug = slug)

    def add_new_tags(self, tag_list, blog_obj):
        """
        Create new tag entries and add it to the given blog entry.
        Skip existing tags and returns only the new created tags.
        """
        new_tags = []
        for tag_name in tag_list:
            try:
                tag_obj = self.get(name = tag_name)
            except self.model.DoesNotExist:
                new_tags.append(tag_name)
                tag_obj = self.create(name = tag_name, slug = tag_name)

            # Add many-to-many
            blog_obj.tags.add(tag_obj)

        return new_tags

    def get_tag_info(self):
        """
        Returns all tags with the additional information:
         * tag.count     - How many blog entries used this tag?

        returns min_frequency and max_frequency, too: The min/max usage of all
        tags. Needed to build a tag cloud.
        """
        tags = self.model.objects.all()
        if not tags:
            # There exist no tags
            return [], 0, 0

        frequency = set()
        # get the counter information
        for tag in tags:
            count = tag.blogentry_set.count()
            tag.count = count
            frequency.add(count)

        min_frequency = float(min(frequency))
        max_frequency = float(max(frequency))

        return tags, min_frequency, max_frequency

#    def get_tag_choices(self):
#        """
#        returns >count< tags witch are the most used tags.
#        """
#        tags, min_frequency, max_frequency = self.get_tag_info()
#
#        tags = sorted(tags, key=lambda x: x.count, reverse=True)
#
#        choices = tuple([(t.id, t.name) for t in tags])
#        return choices


class BlogTag(models.Model):
    """
    A blog entry tag
    TODO: Add a usage counter! So we can easy sort from more to less usages and
          building a tag cloud is easier.
    """
    objects = BlogTagManager()

    name = models.CharField(max_length=255, core=True, unique=True)
    slug = models.SlugField(unique=True, max_length=120)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('name',)


class BlogTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

try:
    admin.site.register(BlogTag, BlogTagAdmin)
except admin.sites.AlreadyRegistered:
    pass # FIXME

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
            content   = self.content,
            context   = context,
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

    class Meta:
        app_label = 'PyLucidPlugins'
        ordering = ('-createtime', '-lastupdatetime')


class BlogEntryAdmin(admin.ModelAdmin):
    pass

try:
    admin.site.register(BlogEntry, BlogEntryAdmin)
except admin.sites.AlreadyRegistered:
    pass # FIXME