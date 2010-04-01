# -*- coding: utf-8 -*-

"""
    PyLucid page update list plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a list of the latest page updates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev$"


from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import Rss201rev2Feed, Atom1Feed
from django.core.urlresolvers import NoReverseMatch

from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.utils.safe_obtain import safe_pref_get_integer
from pylucid_project.apps.pylucid.models import Language, PluginPage

from update_journal.models import UpdateJournal
from update_journal.preference_forms import UpdateJournalPrefForm


def _get_queryset(request, count):
    """ TODO: Move to UpdateJournal.objects ? """
    queryset = UpdateJournal.on_site.all()

    languages = request.PYLUCID.languages
    queryset = queryset.filter(language__in=languages)

    if not request.user.is_staff:
        queryset = queryset.filter(staff_only=False)

    return queryset[:count]


@render_to("update_journal/update_journal_table.html")
def lucidTag(request, count=10):
    try:
        count = int(count)
    except Exception, e:
        if request.user.is_staff:
            request.page_msg.error("page_update_list error: count must be a integer (%s)" % e)
        count = 10

    queryset = _get_queryset(request, count)

    try:
        select_feed_url = PluginPage.objects.reverse("update_journal", "UpdateJournal-select_feed")
    except NoReverseMatch, err:
        select_feed_url = None
        if not settings.DEBUG and request.user.is_staff:
            # PluginPage.objects.reverse creates a page_msg only in DEBUG mode.
            request.page_msg.error(err)

    context = {
        "update_list": queryset,
        "select_feed_url": select_feed_url
    }
    return context


class RssFeed(Feed):
    feed_type = Rss201rev2Feed
    filename = "feed.rss"

    title = _("Update Journal - RSS feed")
    link = "/"
    description_template = "update_journal/feed_description.html"

    def __init__(self, request):
        self.request = request

        # Get max number of feed entries from request.GET["count"]
        # Validate/Limit it with information from DBPreferences 
        self.count, error = safe_pref_get_integer(
            request, "count", UpdateJournalPrefForm,
            default_key="initial_feed_count", default_fallback=5,
            min_key="initial_feed_count", min_fallback=5,
            max_key="max_feed_count", max_fallback=30
        )

    def description(self):
        return _("Last %s updates and changes") % self.count

    def items(self):
        return _get_queryset(self.request, self.count)

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.object_url


class AtomFeed(RssFeed):
    """
    http://docs.djangoproject.com/en/dev/ref/contrib/syndication/#publishing-atom-and-rss-feeds-in-tandem
    """
    feed_type = Atom1Feed
    filename = "feed.atom"
    title = _("Update Journal - Atom feed")
    subtitle = RssFeed.description


# The last class is the fallback class, if filename doesn't match
FEEDS = [AtomFeed, RssFeed]


@render_to("update_journal/select_feed.html")
def select_feed(request):
    """
    Display a list with existing feed filenames.
    """
    context = {"feeds": FEEDS}
    return context


def feed(request, filename):
    """
    return RSS/Atom feed selected by filename.
    """
    #print filename
    for feed_class in FEEDS:
        if filename == feed_class.filename:
            break

    #print "feed class:", feed_class
    feed = feed_class(request)
    response = feed(request)
    return response
