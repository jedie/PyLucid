# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~
    

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-08-11 14:02:53 +0200 (Di, 11 Aug 2009) $
    $Rev: 2263 $
    $Author: JensDiemer $

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev: 2263 $ Alpha"


from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.views.comments import post_comment

from pylucid_project.apps.pylucid.decorators import render_to

from lexicon.models import LexiconEntry




def _add_breadcrumb(request, title, url):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = context["context_middlewares"]["breadcrumb"]
    # Blog entries have only a headline, use it for name and title
    breadcrumb_context_middlewares.add_link(title, title, url)


@render_to("lexicon/summary.html")
def summary(request):
    _add_breadcrumb(request, title="Lexicon summary", url=request.path)

    entries = LexiconEntry.objects.get_filtered_queryset(request)
    context = {
        "entries": entries
    }
    return context


@csrf_protect
@render_to("lexicon/detail_view.html")
def detail_view(request, term=None):

    entry = LexiconEntry.objects.get_entry(request, term, filter_language=False)
    if entry is None:
        # term not exist. page_msg was created.
        return summary(request)

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    if entry.language != request.PYLUCID.language_entry:
        # The Blog article exist in a other language than the client preferred language
        request.page_msg.info(_(
            "Info: This lexicon entry is written in %(article_lang)s."
            " However you prefer %(client_lang)s."
            ) % {
                "article_lang": entry.language.description,
                "client_lang": request.PYLUCID.language_entry.description,
            }
        )

    _add_breadcrumb(request, title="%s: %s" % (entry.term, entry.short_definition), url=request.path)

    # Change permalink from the blog root page to this entry detail view
    permalink = entry.get_permalink(request)
    request.PYLUCID.context["page_permalink"] = permalink # for e.g. the HeadlineAnchor

    context = {
        "entry": entry,
        "page_permalink": permalink, # Change the permalink in the global page template
    }
    return context


@render_to("lexicon/detail_popup.html")
def http_get_view(request):
    term = request.GET["lexicon"]

    entry = LexiconEntry.objects.get_entry(request, term)
    if entry is None:
        # term not exist. page_msg was created.
        return summary(request)

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    context = {"entry": entry}
    return context
