# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import http
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from pylucid_project.apps.pylucid.decorators import render_to, pylucid_objects
from pylucid_project.apps.pylucid.models import PluginPage
from pylucid_project.apps.pylucid.system import i18n

from lexicon.models import LexiconEntry


def _add_breadcrumb(request, title, url):
    """ shortcut for add breadcrumb link """
    context = request.PYLUCID.context
    breadcrumb_context_middlewares = request.PYLUCID.context_middlewares["breadcrumb"]
    # Blog entries have only a headline, use it for name and title
    breadcrumb_context_middlewares.add_link(title, title, url)


@pylucid_objects  # create request.PYLUCID
@render_to("lexicon/summary.html")
def summary(request):
    _add_breadcrumb(request, title="Lexicon summary", url=request.path)

    queryset = LexiconEntry.objects.get_filtered_queryset(request)

    # For adding page update information into context by pylucid context processor
    try:
        # Use the newest lexicon entry
        request.PYLUCID.updateinfo_object = queryset.latest("lastupdatetime")
    except LexiconEntry.DoesNotExist:
        # No blog entries created, yet.
        pass

    context = {
        "entries": queryset
    }
    return context


@pylucid_objects  # create request.PYLUCID
@csrf_protect
@render_to("lexicon/detail_view.html")
def detail_view(request, term=None):

    error_msg = _("Unknown lexicon term.")

    if term in ("", None):  # e.g.: term not in url or GET parameter 'empty'
        if settings.DEBUG or request.user.is_staff:
            error_msg += " (No term given.)"
        messages.error(request, error_msg)
        return

    entry = None
    tried_languages = []
    try:
        queryset = LexiconEntry.on_site.filter(is_public=True)
        queryset = queryset.filter(term=term)
        entry, tried_languages = LexiconEntry.objects.get_by_prefered_language(request, queryset)
    except LexiconEntry.DoesNotExist, err:
        pass

    """
    FIXME: This current solution is boring.
    LexiconEntry.objects.get_by_prefered_language() with i18n.assert_language()
    doesn't do a good job here.
    e.g:
        en + de exists as languages
        user prefered de and called /en/foobar
        foobar does only exist in en not in de
    """

    if entry is None:
        # Entry not found -> Display summary with error message as 404 page
        if settings.DEBUG or request.user.is_staff or settings.PYLUCID.I18N_DEBUG:
            error_msg += " (term: %r, tried languages: %s)" % (term, ", ".join([l.code for l in tried_languages]))
        messages.error(request, error_msg)
        response = summary(request)
        response.status_code = 404  # Send as 404 page, so that search engines doesn't index this.
        return response

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
#        messages.info(request, msg)


    _add_breadcrumb(request, title="%s: %s" % (entry.term, entry.short_definition), url=request.path)

    # Change permalink from the blog root page to this entry detail view
    permalink = entry.get_permalink(request)
    request.PYLUCID.context["page_permalink"] = permalink  # for e.g. the HeadlineAnchor

    # Add comments in this view to the current lexicon entry and not to PageMeta
    request.PYLUCID.object2comment = entry

    # For adding page update information into context by pylucid context processor
    request.PYLUCID.updateinfo_object = entry

    context = {
        "entry": entry,
        "page_permalink": permalink,  # Change the permalink in the global page template
    }
    return context


@pylucid_objects  # create request.PYLUCID
@render_to("lexicon/detail_popup.html")
def http_get_view(request):
    term = request.GET["lexicon"]

    entry = LexiconEntry.objects.get_entry(request, term)
    if entry is None:
        # term not exist. page_msg was created.
        return summary(request)

    try:
        summary_url = PluginPage.objects.reverse("lexicon", "Lexicon-summary")
    except Exception, err:
        if settings.DEBUG:
            messages.error(request, "Can't get summary url: %s" % err)
        summary_url = None

    # Add comments in this view to the current lexicon entry and not to PageMeta
    request.PYLUCID.object2comment = entry

    # For adding page update information into context by pylucid context processor
    request.PYLUCID.updateinfo_object = entry

    context = {
        "entry": entry,
        "summary_url": summary_url,
    }
    return context
