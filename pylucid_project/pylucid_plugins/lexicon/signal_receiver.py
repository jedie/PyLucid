# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"

from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

# http://code.google.com/p/django-tagging/
from tagging.utils import parse_tag_input

from lexicon.models import LexiconEntry
from lexicon.sub_html import SubHtml


WORD_TAG = u"<!-- word -->"


class LexiconData(dict):
    """
    Hold the lexicon data for replacing a lexicon word with a link.
    """
    def __init__(self, *args, **kwargs):
        self._cache = {}
        super(LexiconData, self).__init__(*args, **kwargs)

    def __call__(self, word_lower, word):
        """ called from lexicon.sub_html.SubHtml """
        term = self[word_lower]["term"]
        if term not in self._cache:
            context = {
                "term": term,
                "short_definition": self[word_lower]["short_definition"],
            }
            definition_link = render_to_string("lexicon/definition_link.html", context)
            self._cache[term] = definition_link
        else:
            definition_link = self._cache[term]

        html = definition_link.replace(WORD_TAG, word)
        return html





def pre_render_global_template_handler(**kwargs):
    """
    Handle the 'pre_render_global_template' signal.
    Replace lexicon words in the page_content with a link (with short_definition title)
    to the lexicon.
    """
    request = kwargs["request"]

    current_lang = request.PYLUCID.language_entry
    page_content = request.PYLUCID.context["page_content"]

    queryset = LexiconEntry.on_site.filter(is_public=True).filter(language=current_lang)
    entries = queryset.values_list("term", "alias", "short_definition")

    lexicon_data = LexiconData()
    for term, alias, short_definition in entries:
        aliases = parse_tag_input(alias) # Split django-tagging field value into a python list
        all_words = [term] + aliases
        words_lower = set([word.lower() for word in all_words])

        for word in words_lower:
            lexicon_data[word] = {"term": term, "short_definition": short_definition}

    from lexicon.preference_forms import LexiconPrefForm # import here, against import loops
    pref_form = LexiconPrefForm()
    skip_tags = pref_form.get_skip_tags()

    s = SubHtml(lexicon_data, skip_tags)
    page_content = s.process(page_content)
    request.PYLUCID.context["page_content"] = mark_safe(page_content)


