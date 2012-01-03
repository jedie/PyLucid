# coding:utf-8

"""
    search Blog entries
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.db.models import Q

from blog.models import BlogEntryContent


def get_search_results(request, search_languages, search_strings, search_results):

    queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, tags=None, filter_language=False)

    # Only items in the selected search language
    queryset = queryset.filter(language__in=search_languages)

    for term in search_strings:
        queryset = queryset.filter(
            Q(content__icontains=term) | Q(tags__icontains=term) | Q(headline__icontains=term)
        )

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
            content=item.get_search_content(request),

            # hits in meta content has a higher score, but the content would not displayed 
            meta_content=meta_content,
        )
