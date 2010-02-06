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

from pylucid_project.apps.pylucid.models import Language
from pylucid_project.apps.pylucid.decorators import render_to

from pylucid_project.pylucid_plugins.update_journal.models import UpdateJournal


def _get_queryset(request, count):
    """ TODO: Move to UpdateJournal.objects ? """
    queryset = UpdateJournal.on_site.all()

    accessible_lang = Language.objects.all_accessible(request.user)
    queryset = queryset.filter(language__in=accessible_lang)

    if not request.user.is_staff:
        queryset = queryset.filter(staff_only=False)
 
    return queryset[:count]


@render_to("update_journal/update_journal_table.html")
def lucidTag(request, count=10):
    try:
        count = int(count)
    except Exception, e:
        if request.user.is_stuff():
            request.page_msg.error("page_update_list error: count must be a integer (%s)" % e)
        count = 10

    queryset = _get_queryset(request, count)

    return {"update_list": queryset}


class RssFeed(Feed):
    feed_type = Rss201rev2Feed
    filename = "feed.rss"
    
    title = "Update Journal"
    link = "/"
    description = "Updates and changes"
    description_template = "update_journal/feed_description.html"
    
    def __init__(self, request):
        self.count = 10 # FIXME: use GET parameter?
        self.request = request

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
    