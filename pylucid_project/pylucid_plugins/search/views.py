# coding: utf-8

"""
    PyLucid search plugin
    ~~~~~~~~~~~~~~~~~~~  

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: 2009-07-22 22:49:15 +0200 (Mi, 22 Jul 2009) $
    $Rev: 2151 $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev: 2151 $"

import re

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from pylucid.models import PageTree, PageMeta, PageContent, PluginPage, Design, Language
from pylucid.decorators import render_to

from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.utils.python_tools import cutout

from pylucid_plugins.search.preference_forms import SearchPreferencesForm


pref_form = SearchPreferencesForm()
preferences = pref_form.get_preferences()

#-----------------------------------------------------------------------------

class SearchForm(forms.Form):
    search = forms.CharField(
        min_length=preferences["min_term_len"],
        max_length=preferences["max_term_len"],
    )

class AdvancedSearchForm(SearchForm):
    language = forms.MultipleChoiceField(choices=Language.objects.get_choices())

#-----------------------------------------------------------------------------

def _filter_search_terms(request, search_string):
    """
    Split and filter the search terms.
    """
    raw_search_strings = search_string.split(" ")
    search_strings = []
    for term in raw_search_strings:
        if len(term) < preferences["min_term_len"]:
            request.page_msg("Ignore '%s' (too small)" % term)
        else:
            search_strings.append(term)

    return search_strings


#-----------------------------------------------------------------------------


class SearchHit(object):
    """ one hit entry in the result page """

    text_cutout_len = preferences["text_cutout_len"]
    text_cutout_lines = preferences["text_cutout_lines"]

    def __init__(self, model_instance, search_strings, score, headline, lang, url, content):
        self.model_instance = model_instance
        self.search_strings = search_strings
        self.score = score
        self.headline = headline
        self.lang = lang
        self.url = url
        self.content = content

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

    def _calc_score(self, txt, multiplier):
        score = 0
        for term in self.search_strings_lower:
            score += txt.count(term) * multiplier
        return score

    def add(self, model_instance, headline, lang, url, content, meta_content):
        """
        Add a search hit.
        
        headline - title for the hit in the result list
        lang - language of the hit item, displayed in the result list
        url - absolute url for building a link to the hit item
        content - the main content -> result lines would be cut out from hits in this content
        meta_content - hits in meta content has a higher score, but the content would not displayed 
        """
        score = self._calc_score(content, 1)
        score += self._calc_score(headline, 10)
        score += self._calc_score(meta_content, 5)

        search_hit = SearchHit(
            model_instance=model_instance,
            search_strings=self.search_strings,
            score=score,
            headline=headline,
            lang=lang,
            url=url,
            content=content,
        )

        self.hits.append((score, search_hit))

    def __iter__(self):
        for score, hit in sorted(self.hits, reverse=True):
            yield hit



class Search(object):
    def __init__(self, request):
        self.request = request

    def search(self, search_lang_codes, search_strings):
        """ collect all plugin searches and return the results """
        search_results = SearchResults(self.request, search_strings)
        search_languages = Language.objects.filter(code__in=search_lang_codes)

        # Call every plugin. The plugin adds all results into SearchResults object.
        self.call_searchs(search_languages, search_strings, search_results)

        return search_results

    def call_searchs(self, search_languages, search_strings, search_results):
        """ Call every plugin, witch has the search API. """
        method_kwargs = {
            "search_languages": search_languages,
            "search_strings": search_strings,
            "search_results": search_results
        }

        filename = settings.PYLUCID.SEARCH_FILENAME
        view_name = settings.PYLUCID.SEARCH_VIEWNAME

        for plugin_name, plugin_instance in PYLUCID_PLUGINS.iteritems():
            try:
                plugin_instance.call_plugin_view(self.request, filename, view_name, method_kwargs)
            except Exception, err:
                if not str(err).endswith("No module named %s" % filename):
                    raise


@render_to("search/search.html")#, debug=True)
def http_get_view(request):

    if request.method == 'GET':
        # called from lucidTag
        form_data = request.GET
    else:
        # send own form back
        form_data = request.POST

    if not "language" in form_data:
        # If the client has uses the lucidTag form, there exist no language information
        # -> use the default language 
        form_data._mutable = True
        form_data["language"] = request.PYLUCID.lang_entry.code
        form_data._mutable = False

    form = AdvancedSearchForm(form_data)

    search_results = None

    if form.is_valid():
        search_strings = _filter_search_terms(request, form.cleaned_data["search"])
        if len(search_strings) == 0:
            request.page_msg.error("Error: no search term left, can't search.")
        else:
            search_lang_codes = form.cleaned_data["language"]
            search_results = Search(request).search(search_lang_codes, search_strings)

    context = {
        "page_title": "Advanced search", # Change the global title with blog headline
        "form": form,
        "form_url": request.path + "?search=do_search",
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

