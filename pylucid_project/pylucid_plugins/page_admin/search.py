# coding:utf-8

"""
    search all PageContent pages
"""

from django.contrib.sites.models import Site

from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, PluginPage, Design, Language

def get_search_results(request, search_languages, search_strings, search_results):
    queryset = PageContent.objects

    # search only all pages from this site
    queryset = queryset.filter(pagemeta__pagetree__site=Site.objects.get_current())

    # Filter PageTree view permissions:
    if request.user.is_anonymous(): # Anonymous user are in no user group
        queryset = queryset.filter(pagemeta__pagetree__permitViewGroup=None)
    elif not request.user.is_superuser: # Superuser can see everything ;)
        queryset = queryset.filter(pagemeta__pagetree__permitViewGroup__in=request.user.groups)

    # Only pages in the selected search language
    queryset = queryset.filter(pagemeta__language__in=search_languages)

    for term in search_strings:
        queryset = queryset.filter(content__icontains=term)

    for page in queryset:
        search_results.add(
            model_instance=page,

            # displayed headline of the result hit
            headline=page.get_title(),

            # displayed in the result list
            language=page.pagemeta.language,

            # Link to the hit
            url=page.get_absolute_url(),

            # the main content -> result lines would be cut out from hits in this content
            content=page.content,

            # hits in meta content has a higher score, but the content would not displayed 
            meta_content=page.pagemeta.keywords + " " + page.pagemeta.description,
        )
