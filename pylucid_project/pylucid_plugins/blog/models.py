# coding: utf-8

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core import urlresolvers
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# http://code.google.com/p/django-tagging/
from tagging.models import Tag, TaggedItem

# http://code.google.com/p/django-tools/
from django_tools.middlewares.ThreadLocal import get_current_request
from django_tools.tagging_addon.fields import jQueryTagModelField
from django_tools.template import render
from django_tools.utils.messages import failsafe_message

from pylucid_project.apps.pylucid.fields import MarkupModelField, MarkupContentModelField
from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.models import Language, PluginPage
from pylucid_project.apps.pylucid.models.base_models import AutoSiteM2M, UpdateInfoBaseModel
from pylucid_project.apps.pylucid.system.i18n import change_url_language
from pylucid_project.apps.pylucid.system.permalink import plugin_permalink
from pylucid_project.pylucid_plugins import update_journal
from pylucid_project.utils.i18n_utils import filter_by_language

from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm, get_preferences
from tagging.utils import calculate_cloud, LOGARITHMIC


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class BlogEntry(AutoSiteM2M):
    """
    Language independend Blog entry.
    
    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display
    """
    def __unicode__(self):
        return "Blog entry %i" % self.pk


class BlogEntryContentManager(models.Manager):
    def all_accessible(self, request, filter_language=False):
        """ returns a queryset of all blog entries that the current user can access. """
        filters = self.get_filters(request, filter_language=filter_language)
        return self.model.objects.filter(**filters)

    def get_filters(self, request, filter_language=True):
        """
        Construct queryset filter kwargs, to limit the queryset for the current user
        """
        filters = {"entry__sites__id__exact": settings.SITE_ID}

        if filter_language:
            # Filter by language
            preferences = get_preferences()
            language_filter = preferences["language_filter"]
            if language_filter == BlogPrefForm.CURRENT_LANGUAGE:
                # Display only blog entries in current language (select on the page)             
                filters["language"] = request.PYLUCID.current_language
            elif language_filter == BlogPrefForm.PREFERED_LANGUAGES:
                # Filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)
                filters["language_in"] = request.PYLUCID.current_languages

        if not request.user.has_perm("blog.change_blogentry") or not request.user.has_perm("blog.change_blogentrycontent"):
            filters["is_public"] = True

        return filters

    def get_prefiltered_queryset(self, request, tags=None, filter_language=True):
        filters = self.get_filters(request, filter_language=True)
        queryset = self.model.objects.filter(**filters)

        if tags is not None:
            # filter by tags 
            queryset = TaggedItem.objects.get_by_model(queryset, tags)

        return queryset

    def get_tag_cloud(self, request):
        filters = self.get_filters(request, filter_language=True)
        tag_cloud = Tag.objects.cloud_for_model(self.model, steps=2, filters=filters)
        return tag_cloud

    def cloud_for_queryset(self, queryset, steps=2, distribution=LOGARITHMIC, min_count=None):
        """
        returns the tag cloud for the given queryset
        See: https://code.google.com/p/django-tagging/issues/detail?id=137
        """
        tags = list(
            Tag.objects.usage_for_queryset(queryset, counts=True, min_count=min_count)
        )
        return calculate_cloud(tags, steps, distribution)

    def get_filtered_queryset(self, request, tags=None, filter_language=True):
        queryset = self.get_prefiltered_queryset(request, tags=tags, filter_language=filter_language)

        # To get allways the same paginate count, we create first a list of
        # all BlogEntry ids
        all_entry_ids = tuple(set(queryset.values_list("entry", flat=True)))
        # print "all_entry_ids:", all_entry_ids

        paginator = self.paginate(request, all_entry_ids)
        entry_ids = paginator.object_list
        # print "entry_ids:", entry_ids

        # Create a new QuerySet with all content entries on current paginator page        
        queryset = self.model.objects.filter(entry__in=entry_ids)

        # filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)
        prefered_languages_pk = tuple([lang.pk for lang in request.PYLUCID.languages])
        # print "prefered_languages_pk:", prefered_languages_pk
        queryset = queryset.filter(language__in=prefered_languages_pk)

        # Create a list of content id's which the best language match
        values_list = queryset.values_list("pk", "entry", "language")
        # print "values_list:", values_list
        used_ids = filter_by_language(values_list, prefered_languages_pk)
        # print "used_ids:", used_ids

        # Get the current blog content we display on the current paginator page
        used_content = self.model.objects.filter(pk__in=used_ids)
        paginator.object_list = used_content

        return paginator

    def paginate(self, request, queryset):
        """ Limit the queryset with django Paginator and returns the Paginator instance """
        # Get number of entries allowed by the users see on a page. 
        preferences = get_preferences()
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


class BlogEntryContent(UpdateInfoBaseModel):
    """
    Language depend blog entry content.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = BlogEntryContentManager()

    entry = models.ForeignKey(BlogEntry)

    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )

    content = MarkupContentModelField()
    markup = MarkupModelField()

    language = models.ForeignKey(Language)
    tags = jQueryTagModelField() # a django-tagging model field modified by django-tools
    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def save(self, *args, **kwargs):
        """
        Clean the complete cache.
        
        FIXME: clean only the blog summary and detail page:
            http://www.python-forum.de/topic-22739.html (de)
        """
        super(BlogEntryContent, self).save(*args, **kwargs)

        cache.clear() # FIXME: This cleaned the complete cache for every site!

    def get_html(self):
        """
        return self.content rendered as html:
            1. apply markup
            2. parse lucidTags/django template tags
        """
        content1 = apply_markup(self.content, self.markup, failsafe_message)

        request = get_current_request()
        context = request.PYLUCID.context
        content2 = render.render_string_template(content1, context)

        return content2

    def get_name(self):
        return self.headline

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

        reverse_kwargs = {
            "year": "%s" % self.createtime.year,
            "month": "%s" % self.createtime.month,
            "day": "%s" % self.createtime.day,

#            "year": self.createtime.strftime('%Y'),
#            "month": self.createtime.strftime('%m'),
#            "day": self.createtime.strftime('%d'),

            "id": self.pk, "title":url_title
        }
        print reverse_kwargs
        try:
            # This only worked inner lucidTag
            url = urlresolvers.reverse(viewname, kwargs=reverse_kwargs)
        except urlresolvers.NoReverseMatch, err:
            if settings.RUN_WITH_DEV_SERVER:
                print "*** Blog url reverse error 1: %s" % err
            # Use the first PluginPage instance
            try:
                url = PluginPage.objects.reverse("blog", viewname, kwargs=reverse_kwargs)
            except urlresolvers.NoReverseMatch, err:
                if settings.RUN_WITH_DEV_SERVER:
                    print "*** Blog url reverse error 2: %s" % err
                return "#No-Blog-PagePlugin-exists"

        if not url.startswith("/%s/" % self.language.code):
            # Replace the language code
            # We get the url with the language code from the current session
            # But the entry is written in a other language.
            url = change_url_language(url, self.language.code)

        return url

    def get_permalink(self, request):
        """ permalink to this entry detail view """
        absolute_url = self.get_absolute_url() # Absolute url to this entry
        permalink = plugin_permalink(request, absolute_url)
        return permalink

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')


# Add a entry into update journal
signals.post_save.connect(receiver=update_journal.save_receiver, sender=BlogEntryContent)



# Bug in django tagging?
# http://code.google.com/p/django-tagging/issues/detail?id=151#c2
#try:
#    tagging.register(BlogEntry)
#except tagging.AlreadyRegistered: # FIXME
#    pass
