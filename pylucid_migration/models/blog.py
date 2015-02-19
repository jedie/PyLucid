# coding: utf-8

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages
from django.core import urlresolvers
from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

# http://code.google.com/p/django-tagging/
from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud, LOGARITHMIC

# http://code.google.com/p/django-tools/
from django_tools.models import UpdateInfoBaseModel
from django_tools.tagging_addon.fields import jQueryTagModelField

from pylucid_project.apps.pylucid.models import Language, PluginPage
from pylucid_project.apps.pylucid.system.i18n import change_url_language
from pylucid_project.apps.pylucid.system.permalink import plugin_permalink
from pylucid_project.base_models.base_markup_model import MarkupBaseModel
from pylucid_project.base_models.base_models import BaseModelManager
from pylucid_project.base_models.many2many import SiteM2M
from pylucid_project.pylucid_plugins import update_journal
from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm, get_preferences
from pylucid_project.utils.i18n_utils import filter_by_language




TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


#DEBUG_LANG_FILTER = True
DEBUG_LANG_FILTER = False


class BlogEntry(SiteM2M):
    """
    Language independend Blog entry.
    
    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display
    """
    is_public = models.BooleanField(
        default=True, help_text=_(
            "Is this entry is public viewable?"
            " (If not checked: Every language is non-public,"
            "  otherwise: Public only in the language, if there even set 'is public'.)"
        )
    )

    def save(self, *args, **kwargs):
        """
        Clean the complete cache.
        
        FIXME: clean only the blog summary and detail page:
            http://www.python-forum.de/topic-22739.html (de)
        """
        super(BlogEntry, self).save(*args, **kwargs)

        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

    def get_permalink(self, request, slug=None):
        """
        permalink to this entry (language indepent)
        """
        if slug is None:
            # Add language depend slug, but we didn't use it in permalink_view()
            prefered_languages = request.PYLUCID.languages
            queryset = BlogEntryContent.objects.filter(entry=self).only("slug")
            try:
                slug = queryset.filter(language__in=prefered_languages)[0].slug
            except IndexError:# BlogEntryContent.DoesNotExist
                # no content exist
                return

        reverse_kwargs = {"id": self.id, "slug": slug}
        viewname = "Blog-permalink_view"
        try:
            # This only worked inner lucidTag
            url = urlresolvers.reverse(viewname, kwargs=reverse_kwargs)
        except urlresolvers.NoReverseMatch, err:
            if settings.RUN_WITH_DEV_SERVER:
                print "*** Blog entry url reverse error 1: %s" % err
            # Use the first PluginPage instance
            try:
                url = PluginPage.objects.reverse("blog", viewname, kwargs=reverse_kwargs)
            except urlresolvers.NoReverseMatch, err:
                if settings.RUN_WITH_DEV_SERVER:
                    print "*** Blog entry url reverse error 2: %s" % err
                return "#No-Blog-PagePlugin-exists"

        if hasattr(request.PYLUCID, "pagemeta"):
            # we on the cms pages and not in admin
            permalink = plugin_permalink(request, url)
        else:
            # we are e.g. in admin page
            permalink = url

        return permalink

    def __unicode__(self):
        return "Blog entry %i" % self.pk


class BlogEntryContentManager(BaseModelManager):
    """
    inherited from BaseModelManager:
        get_by_prefered_language() method:
            return a item from queryset in this way:
             - try to get in current language
             - if not exist: try to get in system default language
             - if not exist: use the first found item
    """
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
            if DEBUG_LANG_FILTER:
                messages.debug(request, "language filter: %s" % language_filter)

            if language_filter == BlogPrefForm.CURRENT_LANGUAGE:
                # Display only blog entries in current language (select on the page)             
                filters["language"] = request.PYLUCID.current_language
            elif language_filter == BlogPrefForm.PREFERED_LANGUAGES:
                # Filter by client prefered languages (set in browser and send by HTTP_ACCEPT_LANGUAGE header)
                filters["language__in"] = request.PYLUCID.languages

        if not request.user.has_perm("blog.change_blogentry") or not request.user.has_perm("blog.change_blogentrycontent"):
            filters["entry__is_public"] = True
            filters["is_public"] = True

        if DEBUG_LANG_FILTER:
            messages.debug(request, "queryset filter: %s" % repr(filters))

        return filters

    def get_prefiltered_queryset(self, request, tags=None, filter_language=True):
        if tags is not None:
            # filter by tags
            queryset = TaggedItem.objects.get_by_model(self.model, tags)
        else:
            queryset = self.model.objects.all()

        filters = self.get_filters(request, filter_language=True)
        queryset = queryset.filter(**filters)
        return queryset

    def get_tag_cloud(self, request, filter_language=True):
        filters = self.get_filters(request, filter_language=filter_language)
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

    def paginate(self, request, queryset, max_count):
        """ Limit the queryset with django Paginator and returns the Paginator instance """
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

    def paginator_by_queryset(self, request, queryset, max_count):
        # To get allways the same paginate count, we create first a list of all BlogEntry ids
        all_entry_ids = tuple(queryset.values_list("entry", flat=True))
        # print "all_entry_ids:", all_entry_ids

        paginator = self.paginate(request, all_entry_ids, max_count)
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

    def get_filtered_queryset(self, request, tags=None, filter_language=True):
        """
        returns paginator with all blog entries
        e.g. for summary
        """
        queryset = self.get_prefiltered_queryset(request, tags=tags, filter_language=filter_language)

        # Get number of entries allowed by the users see on a page. 
        preferences = get_preferences()
        if request.user.is_anonymous():
            max_count = preferences.get("max_anonym_count", 10)
        else:
            max_count = preferences.get("max_user_count", 30)

        paginator = self.paginator_by_queryset(request, queryset, max_count)
        return paginator

    def test(self):
        from django.views.generic.date_based import archive_year


class BlogEntryContent(MarkupBaseModel, UpdateInfoBaseModel):
    """
    Language depend blog entry content.

    inherited attributes from MarkupBaseModel:
        content field
        markup field
        get_html() method

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = BlogEntryContentManager()

    entry = models.ForeignKey(BlogEntry)

    language = models.ForeignKey(Language)
    headline = models.CharField(_('Headline'), max_length=255,
        help_text=_("The blog entry headline")
    )
    slug = models.SlugField(max_length=255, blank=True,
        help_text=_(
            "for url (would be set automatically from headline, if emtpy.)"
        ),
    )
    url_date = models.DateField(_('URL Date'), default=now,
        help_text=_("Date used for building the url.")
    )

    tags = jQueryTagModelField() # a django-tagging model field modified by django-tools
    is_public = models.BooleanField(
        default=True, help_text=_("Is entry in this language is public viewable?")
    )

    def clean_fields(self, exclude=None):
        if not self.slug:
            self.slug = slugify(self.headline)

        super(BlogEntryContent, self).clean_fields(exclude)

    def save(self, *args, **kwargs):
        """
        Clean the complete cache.
        
        FIXME: clean only the blog summary and detail page:
            http://www.python-forum.de/topic-22739.html (de)
        """
        self.clean_fields() # for slug field

        super(BlogEntryContent, self).save(*args, **kwargs)

        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

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
        viewname = "Blog-detail_view"

        reverse_kwargs = {
            "year": self.url_date.year,
            "month": "%02i" % self.url_date.month,
            "day": "%02i" % self.url_date.day,
            "slug": self.slug
        }
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
        """ permalink to this entry language indepent """
        permalink = self.entry.get_permalink(request, self.slug)
        return permalink

    def __unicode__(self):
        return self.headline

    class Meta:
        # https://docs.djangoproject.com/en/1.4/ref/models/options/#unique-together
        unique_together = (
            ("language", "url_date", "slug"),
            ("language", "url_date", "headline"),
        )
        ordering = ('-createtime', '-lastupdatetime')


# Add a entry into update journal
signals.post_save.connect(receiver=update_journal.save_receiver, sender=BlogEntryContent)



# Bug in django tagging?
# http://code.google.com/p/django-tagging/issues/detail?id=151#c2
#try:
#    tagging.register(BlogEntry)
#except tagging.AlreadyRegistered: # FIXME
#    pass
