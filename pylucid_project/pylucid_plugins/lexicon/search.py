# coding:utf-8

"""
    search in lexicon entries
"""

from django.contrib.sites.models import Site
from django.db.models import Q

# http://code.google.com/p/django-tagging/
from tagging.utils import parse_tag_input

from lexicon.models import LexiconEntry


def get_search_results(request, search_languages, search_strings, search_results):
    queryset = LexiconEntry.on_site

    # Only public lexicon items:
    queryset = queryset.filter(is_public=True)

    # Only items in the selected search language
    queryset = queryset.filter(language__in=search_languages)

    for term in search_strings:
        queryset = queryset.filter(
            Q(term__icontains=term) | Q(tags__icontains=term) | Q(alias__icontains=term) |
            Q(content__icontains=term) | Q(short_definition__icontains=term)
        )

    for item in queryset:
        meta_content = parse_tag_input(item.tags)
        meta_content += parse_tag_input(item.alias)
        meta_content += [item.term, item.short_definition]
        meta_content = " ".join(meta_content)
        #print "meta: %r" % meta_content

        search_results.add(
            model_instance=item,

            # displayed short_definition of the result hit
            headline="%s: %s" % (item.term, item.short_definition),

            # displayed in the result list
            language=item.language,

            # Link to the hit
            url=item.get_absolute_url(),

            # the main content -> result lines would be cut out from hits in this content
            content=item.content,

            # hits in meta content has a higher score, but the content would not displayed 
            meta_content=meta_content,
        )
