# coding: utf-8

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django.db import models
from django.conf import settings
from django.core import urlresolvers
from django.db.models import signals
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# http://code.google.com/p/django-tagging/
from tagging.fields import TagField

from pylucid_project.apps.pylucid.shortcuts import failsafe_message
from pylucid_project.apps.pylucid.models import PageContent, Language, PluginPage
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.models.base_models import AutoSiteM2M, UpdateInfoBaseModel
from pylucid_project.apps.pylucid.cache import clean_complete_pagecache

from pylucid_project.pylucid_plugins import update_journal

from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm

# from django-tagging
from tagging.models import Tag


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class BlogEntryManager(models.Manager):
    def all_accessible(self, request):
        """ returns a queryset of all blog entries that the current user can access. """
        filters = self.get_filters(request)
        return self.model.objects.filter(**filters)

    def get_filters(self, request):
        """
        Construct queryset filter kwargs, to limit the BlogEntry queryset for the current user
        """
        current_lang = request.PYLUCID.language_entry

        filters = {
            "sites__id__exact": settings.SITE_ID,
            "language": current_lang,
        }

        if not request.user.has_perm("blog.change_blogentry"):
            filters["is_public"] = True

        return filters

    def get_tag_cloud(self, request):
        filters = self.get_filters(request)
        tag_cloud = Tag.objects.cloud_for_model(self.model, steps=2, filters=filters)
        return tag_cloud

    def paginate(self, request, queryset):
        """ Limit the queryset with django Paginator and returns the Paginator instance """
        # Get number of entries allowed by the users see on a page. 
        pref_form = BlogPrefForm()
        preferences = pref_form.get_preferences()
        if request.user.is_anonymous():
            max_count = preferences.get("max_anonym_count", 10)
        else:
            max_count = preferences.get("max_user_count", 30)

        # Show max_count entries per page
        paginator = Paginator(queryset, max_count)

        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        # If page request (9999) is out of range, deliver last page of results.
        try:
            return paginator.page(page)
        except (EmptyPage, InvalidPage):
            return paginator.page(paginator.num_pages)



class BlogEntry(AutoSiteM2M, UpdateInfoBaseModel):
    """
    A blog entry
    
    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = BlogEntryManager()

    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    language = models.ForeignKey(Language)
    markup = models.IntegerField(
        max_length=1, choices=PageContent.MARKUP_CHOICES,
        help_text="the used markup language for this entry",
    )
    tags = TagField(# from django-tagging
        help_text=mark_safe(
            _('tags for this entry. <a href="%s" class="openinwindow"'
            ' title="Information about tag splitting.">tag format help</a>') % TAG_INPUT_HELP_URL
        )
    )
    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
        if not self.is_public: # Don't list non public articles
            return

        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "language": self.language,
            "object_url": self.get_absolute_url(),
            "title": self.headline,
        }

    def get_absolute_url(self):
        url_title = slugify(self.headline)
        viewname = "Blog-detail_view"
        reverse_kwargs = {"id": self.pk, "title":url_title}
        try:
            # This only worked inner lucidTag
            return urlresolvers.reverse(viewname, kwargs=reverse_kwargs)
        except urlresolvers.NoReverseMatch:
            # Use the first PluginPage instance
            try:
                return PluginPage.objects.reverse("blog", viewname, kwargs=reverse_kwargs)
            except urlresolvers.NoReverseMatch:
                return "#No-Blog-PagePlugin-exists"

    def get_html(self):
        """
        returns the generate html code from the content applyed the markup.
        """
        return apply_markup(self.content, self.markup, failsafe_message)

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')


# Add a entry into update journal
signals.post_save.connect(receiver=update_journal.save_receiver, sender=BlogEntry)


# For cleaning the page cache:
signals.post_save.connect(receiver=clean_complete_pagecache, sender=BlogEntry)


# Bug in django tagging?
# http://code.google.com/p/django-tagging/issues/detail?id=151#c2
#try:
#    tagging.register(BlogEntry)
#except tagging.AlreadyRegistered: # FIXME
#    pass
