# coding:utf-8

"""
    search in lexicon entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.db.models import Q

# http://code.google.com/p/django-tagging/
from tagging.utils import parse_tag_input

from pylucid_project.pylucid_plugins.lexicon.models import LexiconEntry


class Search(object):
    def get_queryset(self, request, search_languages, search_strings):
        queryset = LexiconEntry.on_site.select_related()

        # Only public lexicon items:
        queryset = queryset.filter(is_public=True)

        # Only items in the selected search language
        queryset = queryset.filter(language__in=search_languages)

        for term in search_strings:
            queryset = queryset.filter(
                Q(term__icontains=term) | Q(tags__icontains=term) | Q(alias__icontains=term) |
                Q(content__icontains=term) | Q(short_definition__icontains=term)
            )
        return queryset

    def add_search_results(self, request, queryset, search_results):
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
                content=item.get_search_content(request),

                # hits in meta content has a higher score, but the content would not displayed 
                meta_content=meta_content,
            )
