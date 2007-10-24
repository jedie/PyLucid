#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid full text search engine
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Full text search engine for the cms pages.

    TODO:
        * Should search in page title, description and keywords.
        * The constants should be stored into the preferences.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

import time, cgi

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin



# How min. long must a search term be?
MIN_TERM_LEN = 3

# Number of the paged for the result page:
MAX_RESULTS = 20

# The length of the text-hit-cutouts:
TEXT_CUTOUT_LEN = 50

# Max. cutout lines for every search term:
MAX_CUTOUTS_LINES = 5



class SearchForm(forms.Form):
    # TODO: min und max should be saved in the prefereces.
    search_string = forms.CharField(min_length = 3, max_length = 50)


class search(PyLucidBasePlugin):

    def lucidTag(self):
        """
        Insert a empty search form into the page.
        """
        search_form = SearchForm()
        context = {
            "url": self.URLs.methodLink("do_search"),
            "search_form": search_form,
        }
        self._render_template("input_form", context)


    def do_search(self):
        """
        Answer a search POST.
        """
        # Change the global page title:
        self.context["PAGE"].title = _("page search")

        context = {}

        if self.request.method == 'POST':
            search_form = SearchForm(self.request.POST)
            if search_form.is_valid():
                search_string = search_form.cleaned_data["search_string"]
                try:
                    search_strings = self._filter_search_terms(search_string)
                except WrongSearchTerm, msg:
                    self.page_msg.red(msg)
                else:
                    #self.page_msg("Used search terms:", search_strings)
                    start_time = time.time()
                    # Search in the database:
                    hits, results = self._search(search_strings)

                    self._add_content_extract(results, search_strings)

                    context["duration"] = time.time() - start_time
                    context["hits"] = hits
                    context["results"] = results
                    context["search_string"] = search_string
        else:
            search_form = SearchForm()

        context["search_form"] = search_form

        self._render_template("result_page", context)


    def _filter_search_terms(self, search_string):
        """
        Split and filter the search terms.
        """
        raw_search_strings = search_string.split(" ")
        search_strings = []
        for term in raw_search_strings:
            if len(term)<MIN_TERM_LEN:
                self.page_msg("Ignore '%s' (too small)" % cgi.escape(term))
            else:
                search_strings.append(term)

        if len(search_strings) == 0:
            raise WrongSearchTerm("Error: no search term left, can't search.")

        return search_strings


    def _search(self, search_strings):
        """
        Process the search and retuned the results.
        """
        pages = Page.objects.all().filter(showlinks = True)
        if self.request.user.is_anonymous():
            pages = pages.exclude(permitViewPublic = False)

        for term in search_strings:
            pages = pages.filter(content__icontains=term)

        # Value the hits. Make a sortable tuple.
        results = []
        for page in pages:
            score = 0
            content = page.content

            for term in search_strings:
                score += content.count(term)

            results.append((score, page))

        # Count the total hits:
        hits = len(results)

        # sort the hits.
        results.sort(reverse=True)

        # Use only the first pages:
        results = results[:MAX_RESULTS]

        # Build a dict, for the template
        results = [{"score": p[0], "page": p[1]} for p in results]

        return hits, results


    def _add_content_extract(self, results, search_strings):
        """
        cut the hits in the page content out. So the template can display
        the lines.
        """
        def escape(txt):
            txt = cgi.escape(txt)
            # Escape django template tags chars "{" and "}" to the HTML
            # character entity:
            txt = txt.replace("{", "&#x7B;").replace("}", "&#x7D;")
            return txt


        for result in results:
            result["cutouts"] = []
            content = result["page"].content

            for term in search_strings:
                start = 0
                for _ in xrange(MAX_CUTOUTS_LINES):
                    try:
                        index = content.index(term, start)
                    except ValueError:
                        # No more hits in the page content
                        break

                    start = index+1

                    if index<TEXT_CUTOUT_LEN:
                        txt = content[:TEXT_CUTOUT_LEN]
                    else:
                        txt = content[index-TEXT_CUTOUT_LEN:index+TEXT_CUTOUT_LEN]

                    txt = escape(txt)
                    txt = txt.replace(term, "<strong>%s</strong>" % term)
                    result["cutouts"].append(txt)


class WrongSearchTerm(Exception):
    pass