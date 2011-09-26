# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    http://feedvalidator.org/
    
    TODO:
        * Detail view, use BlogEntry.get_absolute_url()

    :copyleft: 2008-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.conf import settings
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core import urlresolvers
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.feedgenerator import Rss201rev2Feed, Atom1Feed
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic.date_based import archive_year, archive_month

from pylucid_project.apps.pylucid.system import i18n
from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.utils.safe_obtain import safe_pref_get_integer

from pylucid_project.pylucid_plugins.blog.models import BlogEntry, \
    BlogEntryContent
from pylucid_project.pylucid_plugins.blog.preference_forms import BlogPrefForm

# from django-tagging
from tagging.models import Tag, TaggedItem



def _add_breadcrumb(request, *args, **kwargs):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    try:
        breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    except KeyError:
        # No breadcrumbs used in current template
        return
    breadcrumb_context_middlewares.add_link(*args, **kwargs)


#def _get_queryset(request, tags=None, filter_language=False):
#    # Get all blog entries, that the current user can see
#    queryset = BlogEntry.objects.all_accessible(request, filter_language=filter_language)
#
#    if tags is not None:
#        # filter by tags 
#        queryset = TaggedItem.objects.get_by_model(queryset, tags)
#
#    return queryset


def _split_tags(raw_tags):
    "simple split tags from url"
    tags = raw_tags.strip("/").split("/")
    return tags


class RssFeed(Feed):
    feed_type = Rss201rev2Feed
    filename = "feed.rss"
    title = _("Blog - RSS feed")
    link = "/"
    description_template = "blog/feed_description.html"

    def __init__(self, request, tags=None):
        self.request = request
        # client favored Language instance:
        lang_entry = request.PYLUCID.current_language
        self.language = lang_entry.code

        if tags is not None:
            tags = _split_tags(tags)
        self.tags = tags

        # Get max number of feed entries from request.GET["count"]
        # Validate/Limit it with information from DBPreferences 
        self.count, error = safe_pref_get_integer(
            request, "count", BlogPrefForm,
            default_key="initial_feed_count", default_fallback=5,
            min_key="initial_feed_count", min_fallback=5,
            max_key="max_feed_count", max_fallback=30
        )

    def description(self):
        if self.tags is None:
            return _("Last %s blog articles") % self.count
        else:
            return _(
                 "Last %(count)s blog articles tagged with: %(tags)s"
            ) % {"count":self.count, "tags": ",".join(self.tags)}

    def items(self):
        queryset = _get_queryset(self.request, self.tags, filter_language=True)
        return queryset[:self.count]

    def item_title(self, item):
        return item.headline

    def item_author_name(self, item):
        return item.createby

    def item_link(self, item):
        return item.get_absolute_url()


class AtomFeed(RssFeed):
    """
    http://docs.djangoproject.com/en/dev/ref/contrib/syndication/#publishing-atom-and-rss-feeds-in-tandem
    """
    feed_type = Atom1Feed
    filename = "feed.atom"
    title = _("Blog - Atom feed")
    subtitle = RssFeed.description


FEEDS = (AtomFeed, RssFeed)
FEED_FILENAMES = (AtomFeed.filename, RssFeed.filename)



@render_to("blog/summary.html")
def summary(request):
    """
    Display summary list with all blog entries.
    """
    # Get all blog entries, that the current user can see
    paginator = BlogEntryContent.objects.get_filtered_queryset(request, filter_language=True)

    # Calculate the tag cloud from all existing entries
    tag_cloud = BlogEntryContent.objects.get_tag_cloud(request)

    _add_breadcrumb(request, _("All articles."))

    # For adding page update information into context by pylucid context processor
    try:
        # Use the newest blog entry for date info
        request.PYLUCID.updateinfo_object = paginator.object_list[0]
    except BlogEntry.DoesNotExist:
        # No blog entries created, yet.
        pass

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "filenames": FEED_FILENAMES,
    }
    return context


@render_to("blog/summary.html")
def tag_view(request, tags):
    """
    Display summary list with blog entries filtered by the given tags.
    """
    tags = _split_tags(tags)

    # Get all blog entries, that the current user can see
    paginator = BlogEntryContent.objects.get_filtered_queryset(request, tags=tags, filter_language=True)

    # Calculate the tag cloud from the current used queryset
    queryset = paginator.object_list
    tag_cloud = BlogEntryContent.objects.cloud_for_queryset(queryset)

    # Add link to the breadcrumbs ;)
    text = _("All items tagged with: %s") % ", ".join(["'%s'" % tag for tag in tags])
    _add_breadcrumb(request, text)

    # For adding page update information into context by pylucid context processor
    try:
        # Use the newest blog entry for date info
        request.PYLUCID.updateinfo_object = paginator.object_list[0]
    except BlogEntry.DoesNotExist:
        # No blog entries created, yet.
        pass

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "add_tag_filter_link": True, # Add + tag filter link
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "used_tags": tags,
        "tags": "/".join(tags),
        "filenames": FEED_FILENAMES,
    }
    return context


@csrf_protect
@render_to("blog/detail_view.html")
def detail_view(request, year, month, day, slug):
    """
    Display one blog entry with a comment form.
    """
    # Get all blog entries, that the current user can see
    prefiltered_queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, filter_language=False)

    try:
        entry = prefiltered_queryset.get(createtime__year=year, createtime__month=month, createtime__day=day, slug=slug)
    except BlogEntryContent.DoesNotExist:
        # XXX: redirect to day_archive() ?
        # It's possible that the user comes from a external link.
        messages.error(request, _("Entry for this url doesn't exist."))
        url = urlresolvers.reverse("Blog-summary")
        return HttpResponseRedirect(url)

#    new_url = i18n.assert_language(request, entry.language)
#    if new_url:
#        # the current language is not the same as entry language -> redirect to right url
#        # e.g. someone followed a external link to this article, but his preferred language
#        # is a other language as this article. Activate the article language and "reload"
#        return http.HttpResponsePermanentRedirect(new_url)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, entry.headline, _("Article '%s'") % entry.headline)

    # Calculate the tag cloud from all existing entries
    tag_cloud = BlogEntryContent.objects.get_tag_cloud(request)

    # Change permalink from the blog root page to this entry detail view
    permalink = entry.get_permalink(request)
    request.PYLUCID.context["page_permalink"] = permalink # for e.g. the HeadlineAnchor

    # Add comments in this view to the current blog entry and not to PageMeta
    request.PYLUCID.object2comment = entry

    # For adding page update information into context by pylucid context processor
    request.PYLUCID.updateinfo_object = entry

    context = {
        "page_title": entry.headline, # Change the global title with blog headline
        "entry": entry,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "page_permalink": permalink, # Change the permalink in the global page template
    }
    return context

#------------------------------------------------------------------------------

def permalink_view(request, id, slug=None):
    """ redirect to language depent blog entry """
    prefiltered_queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, filter_language=False)

    prefered_languages = request.PYLUCID.languages

    prefiltered_queryset = prefiltered_queryset.filter(entry__id__exact=id)
    try:
        entry = prefiltered_queryset.filter(language__in=prefered_languages)[0]
    except BlogEntry.DoesNotExist:
        # wrong permalink -> display summary
        msg = "Blog entry doesn't exist."
        if settings.DEBUG or request.user.is_staff:
            msg += " (ID %r wrong.)" % id
        messages.error(request, msg)
        return summary(request)

    url = entry.get_absolute_url()
    return HttpResponsePermanentRedirect(url)

#------------------------------------------------------------------------------

def redirect_old_urls(request, id, title):
    """ permanent redirect old url's to new url scheme """
    prefiltered_queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, filter_language=False)

    try:
        entry = prefiltered_queryset.get(pk=id)
    except BlogEntry.DoesNotExist:
        # It's possible that the user comes from a external link.
        msg = "Blog entry doesn't exist."
        if settings.DEBUG or request.user.is_staff:
            msg += " (ID %r wrong.)" % id
        messages.error(request, msg)
        return summary(request)

    url = entry.get_absolute_url()
    return HttpResponsePermanentRedirect(url)

def year_archive(request, year):
    queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, filter_language=False)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, _("%s archive") % year, _("All article from year %s") % year)

    context = {
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return archive_year(
        request, year, queryset, date_field="createtime", extra_context=context,
        make_object_list=True
    )

def month_archive(request, year, month):
    print "***"
    queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, filter_language=False)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, _("%s.%s archive") % (year, month), _("All article from %s.%s") % (year, month))

    context = {
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
    }
    return archive_month(
        request, year, month, queryset, date_field="createtime", extra_context=context,
        month_format="%m", allow_empty=True
    )

def day_archive(request, year, month, day):
    raise NotImplementedError

#------------------------------------------------------------------------------


@render_to("blog/select_feed.html")
def select_feed(request):
    """ Display a list with existing feed filenames. """
    context = {"filenames": FEED_FILENAMES}
    return context


def feed(request, filename, tags=None):
    """
    return RSS/Atom feed for all blog entries and filtered by tags. 
    Feed format is selected by filename.
    """
    for feed_class in FEEDS:
        if filename == feed_class.filename:
            break

    # client favoured Language instance:
    lang_entry = request.PYLUCID.current_language

    # Work-a-round for http://code.djangoproject.com/ticket/13896
    old_lang_code = settings.LANGUAGE_CODE
    settings.LANGUAGE_CODE = lang_entry.code

    feed = feed_class(request, tags)
    response = feed(request)

    settings.LANGUAGE_CODE = old_lang_code

    return response

