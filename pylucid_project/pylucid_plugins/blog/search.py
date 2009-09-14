# coding:utf-8

"""
    search all PageContent pages
"""

from django.contrib.sites.models import Site

from tagging.utils import parse_tag_input

from blog.models import BlogEntry


def get_search_results(request, search_languages, search_strings, search_results):
    queryset = BlogEntry.on_site

    # Only public blog items:
    queryset = queryset.filter(is_public=True)

    # Only items in the selected search language
    queryset = queryset.filter(language__in=search_languages)

    for term in search_strings:
        queryset = queryset.filter(content__icontains=term)

    for item in queryset:
        meta_content = item.tags
        #print "meta: %r" % meta_content

        search_results.add(
            model_instance=item,

            # displayed headline of the result hit
            headline=item.headline,

            # displayed in the result list
            language=item.language,

            # Link to the hit
            url=item.get_absolute_url(),

            # the main content -> result lines would be cut out from hits in this content
            content=item.content,

            # hits in meta content has a higher score, but the content would not displayed 
            meta_content=meta_content,
        )
