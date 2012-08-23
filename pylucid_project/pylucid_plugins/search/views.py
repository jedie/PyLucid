# coding: utf-8

"""
    PyLucid search plugin
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import time
import traceback


from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

# http://code.google.com/p/django-tagging/
from tagging.utils import parse_tag_input

from django_tools.template.filters import human_duration

from pylucid_project.apps.pylucid.context_processors import NowUpdateInfo
from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.apps.pylucid.models import Language, LogEntry
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS, \
    PluginNotOnSite
from pylucid_project.utils.python_tools import cutout

from pylucid_project.pylucid_plugins.search.preference_forms import get_preferences
from pylucid_project.pylucid_plugins.search.forms import AdvancedSearchForm, \
    SearchForm


def _filter_search_terms(request, search_string):
    """
    Split and filter the search terms.
    """
    preferences = get_preferences()

    raw_search_strings = parse_tag_input(search_string) # split with django-tagging
    search_strings = []
    for term in raw_search_strings:
        if len(term) < preferences["min_term_len"]:
            messages.warning(request, "Ignore '%s' (too small)" % term)
        else:
            search_strings.append(term)

    return search_strings


#-----------------------------------------------------------------------------


class SearchHit(object):
    """ one hit entry in the result page """
    def __init__(self, model_instance, search_strings, score, headline, language, url, content, preferences):
        self.model_instance = model_instance
        self.search_strings = search_strings
        self.score = score
        self.headline = headline
        self.language = language
        self.url = url
        self.content = strip_tags(content)

        self.text_cutout_len = preferences["text_cutout_len"]
        self.text_cutout_lines = preferences["text_cutout_lines"]

    def content_type(self):
        content_type = ContentType.objects.get_for_model(self.model_instance)
        return content_type

    def cutouts(self):
        """
        display the hits in the result page.
        cut the hits in the page content out. So the template can display
        the lines.
        """
        cutout_lines = []

        cutouts = cutout(
            content=self.content,
            terms=self.search_strings,
            max_lines=self.text_cutout_lines,
            cutout_len=self.text_cutout_len,
        )
        for pre_txt, hit_txt, post_txt in cutouts:
            yield (pre_txt, hit_txt, post_txt)


#-----------------------------------------------------------------------------


class SearchResults(object):
    """
    holds the search result data
    """
    def __init__(self, request, search_strings):
        self.request = request
        self.search_strings = search_strings
        self.search_strings_lower = tuple([i.lower() for i in search_strings])
        self.hits = []

        self.duration = None # set in self.done()
        self.plugin_count = None # set in self.done()
        self.start_time = time.time()

        self.preferences = get_preferences()

    def _calc_score(self, txt, multiplier):
        score = 0
        for term in self.search_strings_lower:
            score += txt.count(term) * multiplier
        return score

    def add(self, model_instance, headline, language, url, content, meta_content):
        """
        Add a search hit.
        
        headline - title for the hit in the result list
        language - language of the hit item, displayed in the result list
        url - absolute url for building a link to the hit item
        content - the main content -> result lines would be cut out from hits in this content
        meta_content - hits in meta content has a higher score, but the content would not displayed 
        """
        score = self._calc_score(content, 1)
        score += self._calc_score(headline, 10)
        score += self._calc_score(meta_content, 5)

        if language == self.request.PYLUCID.current_language:
            # Multiply the score if the content language
            # is the same as client prefered language 
            score *= 2

        search_hit = SearchHit(
            model_instance=model_instance,
            search_strings=self.search_strings,
            score=score,
            headline=headline,
            language=language,
            url=url,
            content=content,
            preferences=self.preferences,
        )

        self.hits.append((score, search_hit))

    def done(self, plugin_count, use_plugin, too_much_hits):
        self.plugin_count = plugin_count
        self.use_plugin = use_plugin
        self.too_much_hits = too_much_hits

        self.duration = time.time() - self.start_time

    def __iter__(self):
        for score, hit in sorted(self.hits, reverse=True):
            yield hit


class Search(object):
    def __init__(self, request, preferences):
        self.request = request
        self.preferences = preferences

    def search(self, search_lang_codes, search_strings):
        """ collect all plugin searches and return the results """
        search_results = SearchResults(self.request, search_strings)
        search_languages = Language.objects.filter(code__in=search_lang_codes)
#        search_languages = Language.objects.all_accessible().filter(code__in=search_lang_codes)

        # Call every plugin. The plugin adds all results into SearchResults object.
        plugin_count, use_plugin, too_much_hits = self.call_searchs(search_languages, search_strings, search_results)

        search_results.done(plugin_count, use_plugin, too_much_hits)

        return search_results

    def call_searchs(self, search_languages, search_strings, search_results):
        """ Call every plugin, witch has the search API. """
        filename = settings.PYLUCID.SEARCH_FILENAME
        class_name = settings.PYLUCID.SEARCH_CLASSNAME

        max_hits = self.preferences["max_hits"]

        plugin_count = 0
        too_much_hits = 0
        use_plugin = 0
        for plugin_name, plugin_instance in PYLUCID_PLUGINS.iteritems():
            try:
                SearchClass = plugin_instance.get_plugin_object(filename, class_name)
#                plugin_instance.call_plugin_view(self.request, filename, view_name, method_kwargs)
            except plugin_instance.ObjectNotFound:
                # Plugin has no search API
                continue
            except Exception:
                if self.request.debug or self.request.user.is_staff:
                    messages.error(self.request, "Can't collect search results from %s." % plugin_name)
                    messages.debug(self.request, mark_safe("<pre>%s</pre>" % traceback.format_exc()))
                continue

            try:
                search_instance = SearchClass()
            except PluginNotOnSite, err:
                # Plugin is not used on this SITE
                if self.request.debug or self.request.user.is_staff:
                    messages.debug(self.request, "Skip %s: %s" % (plugin_name, err))
                continue
            else:
                plugin_count += 1

            queryset = search_instance.get_queryset(self.request, search_languages, search_strings)
            count = queryset.count()
            if self.request.user.is_staff:
                messages.info(self.request, "%s hits in %s" % (count, plugin_name))

            if count >= max_hits:
                too_much_hits += 1
                messages.info(self.request, "Skip too many results from %s" % plugin_name)
                LogEntry.objects.log_action(
                    app_label="search", action="too mutch hits",
                    message="Skip %s hits in %s for %s" % (count, plugin_name, repr(search_strings)),
                    data={
                        "search_strings": search_strings,
                        "hits": count,
                    }
                )
                continue

            use_plugin += 1

            if count > 0:
                search_instance.add_search_results(self.request, queryset, search_results)

        return plugin_count, use_plugin, too_much_hits


def _search(request, cleaned_data):
    search_strings = _filter_search_terms(request, cleaned_data["search"])
    if len(search_strings) == 0:
        messages.error(request, "Error: no search term left, can't search.")
        return

    preferences = get_preferences()
    min_pause = preferences["min_pause"]
    ban_limit = preferences["ban_limit"]

    try:
        LogEntry.objects.request_limit(request, min_pause, ban_limit, app_label="search")
    except LogEntry.RequestTooFast:
        # min_pause is not observed, page_msg has been created -> don't search
        return

    search_lang_codes = cleaned_data["language"]
    search_results = Search(request, preferences).search(search_lang_codes, search_strings)
    hits_count = len(search_results.hits)
    duration = human_duration(search_results.duration)
    msg = "done in %s, %s hits for: %r" % (duration, hits_count, search_strings)
    LogEntry.objects.log_action(
        app_label="search", action="search done", message=msg,
        data={
            "search_strings": search_strings,
            "duration": search_results.duration,
            "hits": hits_count,
        }
    )
    return search_results


@csrf_exempt # FIXME: Use AJAX?
@render_to("search/search.html")#, debug=True)
def http_get_view(request):

    # XXX: Should we support GET search ?

    if "search_page" in request.POST:
        # Form send by search page
        querydict = request.POST
    else:
        # Form was send by lucidTag -> set default search language

        querydict = request.POST.copy() # make POST QueryDict mutable

        preferences = get_preferences()
        use_all_languages = preferences["all_languages"]

        if use_all_languages:
            # use all accessible languages
            accessible_languages = Language.objects.all_accessible(request.user)
            codes = accessible_languages.values_list('code', flat=True)
            querydict.setlist("language", codes)
        else:
            # preselect only the client preferred language
            querydict["language"] = request.PYLUCID.current_language.code

    form = AdvancedSearchForm(querydict)

    if form.is_valid():
        search_results = _search(request, form.cleaned_data)
    else:
        search_results = None

    # For adding page update information into context by pylucid context processor
    request.PYLUCID.updateinfo_object = NowUpdateInfo(request)

    context = {
        "page_title": "Advanced search", # Change the global title with blog headline
        "form": form,
        "form_url": request.path + "?search=",
        "search_results": search_results,
    }
    return context


@render_to("search/lucidTag.html")#, debug=True)
def lucidTag(request):
    """
    Display only a small search form. Can be inserted into the globale page template.
    The form is a GET form, so http_get_view() handle it.
    """
    return {"form": SearchForm()}

