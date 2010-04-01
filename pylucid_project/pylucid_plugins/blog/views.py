# coding: utf-8

"""
    PyLucid blog plugin
    ~~~~~~~~~~~~~~~~~~~

    A simple blog system.

    http://feedvalidator.org/
    
    TODO:
        * Detail view, use BlogEntry.get_absolute_url()
    

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev$"


from django import http
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.views.comments import post_comment
from django.utils.feedgenerator import Rss201rev2Feed, Atom1Feed

from pylucid_project.apps.pylucid.system import i18n
from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.utils.safe_obtain import safe_pref_get_integer

from blog.models import BlogEntry
from blog.preference_forms import BlogPrefForm

# from django-tagging
from tagging.models import Tag, TaggedItem



def _add_breadcrumb(request, *args, **kwargs):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    breadcrumb_context_middlewares.add_link(*args, **kwargs)


def _get_queryset(request, tags=None, filter_language=False):
    # Get all blog entries, that the current user can see
    queryset = BlogEntry.objects.all_accessible(request, filter_language=filter_language)

    if tags is not None:
        # filter by tags 
        queryset = TaggedItem.objects.get_by_model(queryset, tags)

    return queryset


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


# The last class is the fallback class, if filename doesn't match
FEEDS = [AtomFeed, RssFeed]



@render_to("blog/summary.html")
def summary(request):
    """
    Display summary list with all blog entries.
    """
    # Get all blog entries, that the current user can see
    queryset = _get_queryset(request, filter_language=True)

    # Limit the queryset with django Paginator
    paginator = BlogEntry.objects.paginate(request, queryset)

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    current_lang = request.PYLUCID.current_language.description
    _add_breadcrumb(request, _("All blog articles in %s.") % current_lang)

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "feeds": FEEDS,
    }
    return context


@render_to("blog/summary.html")
def tag_view(request, tags):
    """
    Display summary list with blog entries filtered by the given tags.
    """
    tags = _split_tags(tags)

    # Get all blog entries, that the current user can see
    queryset = _get_queryset(request, tags, filter_language=True)

    # Limit the queryset with django Paginator
    paginator = BlogEntry.objects.paginate(request, queryset)

    # Add link to the breadcrumbs ;)
    text = _("All items tagged with: %s") % ", ".join(tags)
    current_lang = request.PYLUCID.current_language.description
    _add_breadcrumb(request, text, text + _(" and are written in %s.") % current_lang)

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    context = {
        "entries": paginator,
        "tag_cloud": tag_cloud,
        "add_tag_filter_link": True, # Add + tag filter link
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "used_tags": tags,
        "tags": "/".join(tags),
        "feeds": FEEDS,
    }
    return context


@csrf_protect
@render_to("blog/detail_view.html")
def detail_view(request, id, title):
    """
    Display one blog entry with a comment form.
    """
    # Get all blog entries, that the current user can see
    queryset = _get_queryset(request, filter_language=False)

    try:
        entry = queryset.get(pk=id)
    except BlogEntry.DoesNotExist:
        # It's possible that the user comes from a external link.
        msg = "Blog entry doesn't exist."
        if settings.DEBUG or request.user.is_staff:
            msg += " (ID %r wrong.)" % id
        request.page_msg.error(msg)
        return summary(request)

    new_url = i18n.assert_language(request, entry.language)
    if new_url:
        # the current language is not the same as entry language -> redirect to right url
        # e.g. someone followed a external link to this article, but his preferred language
        # is a other language as this article. Activate the article language and "reload"
        return http.HttpResponsePermanentRedirect(new_url)

    # Add link to the breadcrumbs ;)
    _add_breadcrumb(request, entry.headline, _("Blog article '%s'") % entry.headline)

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    tag_cloud = BlogEntry.objects.get_tag_cloud(request)

    # Change permalink from the blog root page to this entry detail view
    permalink = entry.get_permalink(request)
    request.PYLUCID.context["page_permalink"] = permalink # for e.g. the HeadlineAnchor

    context = {
        "page_title": entry.headline, # Change the global title with blog headline
        "entry": entry,
        "tag_cloud": tag_cloud,
        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,
        "page_permalink": permalink, # Change the permalink in the global page template
    }
    return context

#------------------------------------------------------------------------------


@render_to("blog/select_feed.html")
def select_feed(request):
    """ Display a list with existing feed filenames. """
    context = {"feeds": FEEDS}
    return context


def feed(request, filename, tags=None):
    """
    return RSS/Atom feed for all blog entries and filtered by tags. 
    Feed format is selected by filename.
    """
    for feed_class in FEEDS:
        if filename == feed_class.filename:
            break

    feed = feed_class(request, tags)
    response = feed(request)
    return response

