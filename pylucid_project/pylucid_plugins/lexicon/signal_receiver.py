# coding: utf-8

"""
    PyLucid lexicon plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    signal receiver, connected in lexicon.__init__.py
    Search in the page_content for all lexicon terms and
    replace them with a link.
    
    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"

import sys
import traceback
import HTMLParser
from xml.sax.saxutils import escape

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
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

    def __call__(self, matchobject):
        """
        called from lexicon.sub_html.SubHtml
        
        We render a lexicon link in two steps, because the actual replaced word
        for a term can be vary in spelling. So in the first step, we render
        everything except the original word and cached this. In the second we
        replaced the placeholder with the real word.
        """
        word = matchobject.group(0) # The original word
        data = self[word.lower()] # get the lexicon data for this word
        term = data["term"] # The lexicon term for this word
        if term not in self._cache:
            context = {
                "term": term,
                "short_definition": data["short_definition"],
            }
            # Render the lexicon link without the original word.
            definition_link = render_to_string("lexicon/definition_link.html", context)
            self._cache[term] = definition_link
        else:
            definition_link = self._cache[term]

        # Replace the placeholder with the original word.
        html = definition_link.replace(WORD_TAG, word)
        return html


def pre_render_global_template_handler(**kwargs):
    """
    Handle the 'pre_render_global_template' signal.
    Replace lexicon words in the page_content with a link (with short_definition title)
    to the lexicon.
    """
    request = kwargs["request"]

    current_lang = request.PYLUCID.current_language
    page_content = request.PYLUCID.context["page_content"]

    queryset = LexiconEntry.on_site.filter(is_public=True).filter(language=current_lang)
    entries = queryset.values_list("term", "alias", "short_definition")

    lexicon_data = LexiconData()
    for term, alias, short_definition in entries:
        aliases = parse_tag_input(alias) # Split django-tagging field value into a Python list
        all_words = [term] + aliases
        words_lower = set([word.lower() for word in all_words])

        for word in words_lower:
            lexicon_data[word] = {"term": term, "short_definition": short_definition}

    if not lexicon_data:
        # No lexicon entries -> nothing to do
        return

    from lexicon.preference_forms import LexiconPrefForm # import here, against import loops
    pref_form = LexiconPrefForm()
    skip_tags = pref_form.get_skip_tags()

    s = SubHtml(lexicon_data, skip_tags)

    try:
        s.feed(page_content)
    except HTMLParser.HTMLParseError, err:
        # HTMLParser can only parse valid HTML code.
        err = escape(str(err))
        msg = _("Wrong HTML code")
        if settings.DEBUG:
            # insert more information into the traceback and re-raise the original error
            # XXX: http://code.djangoproject.com/ticket/13029 - Exception Value is empty in traceback page.
            etype, evalue, etb = sys.exc_info()
            evalue = etype('%s: %s' % (msg, err))
            raise etype, evalue, etb

        if request.user.is_staff: # add more info for staff members
            msg += u" (%s)" % err

        if request.user.is_superuser:
            # put the full traceback into page_msg, but only for superusers
            request.page_msg(mark_safe("%s:<pre>%s</pre>" % (msg, traceback.format_exc())))
    else:
        page_content = s.html # Get the html code with the lexicon links
        # Update the page content:
        request.PYLUCID.context["page_content"] = mark_safe(page_content)


