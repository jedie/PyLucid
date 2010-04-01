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


from django import http
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.views.comments import post_comment

from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.apps.pylucid.system import i18n

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

    error_msg = _("Unknown lexicon term.")

    if term in ("", None): # e.g.: term not in url or GET parameter 'empty'
        if settings.DEBUG or request.user.is_staff:
            error_msg += " (No term given.)"
        request.page_msg.error(error_msg)
        return

    queryset = LexiconEntry.on_site.filter(is_public=True)
    queryset = queryset.filter(term=term)

    entry, tried_languages = LexiconEntry.objects.get_by_prefered_language(request, queryset)

    if entry is None:
        if settings.DEBUG or request.user.is_staff or settings.PYLUCID.I18N_DEBUG:
            error_msg += " (term: %r, tried languages: %s)" % (term, ", ".join([l.code for l in tried_languages]))
        request.page_msg.error(error_msg)
        return summary(request)

    if request.POST:
        # Use django.contrib.comments.views.comments.post_comment to handle a comment
        # post.
        return post_comment(request, next=entry.get_absolute_url())

    new_url = i18n.assert_language(request, entry.language, check_url_language=True)
    if new_url:
        # the current language is not the same as entry language -> redirect to right url
        # e.g. someone followed a external link to this article, but his preferred language
        # is a other language as this article. Activate the article language and "reload"
        return http.HttpResponseRedirect(new_url)

#    if entry.language != request.PYLUCID.current_language:
#        # The item exist in a other language than the client preferred language
#        msg = _(
#            "Info: This lexicon entry is written in %(article_lang)s."
#            " However you prefer %(client_lang)s."
#        ) % {
#            "article_lang": entry.language.description,
#            "client_lang": request.PYLUCID.current_language.description,
#        }
#        if settings.DEBUG or request.user.is_staff or settings.PYLUCID.I18N_DEBUG:
#            msg += "(tried languages: %s)" % ", ".join([l.code for l in tried_languages])
#        request.page_msg.info(msg)


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
