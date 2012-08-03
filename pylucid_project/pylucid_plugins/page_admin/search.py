# coding:utf-8

"""
    search PageContent
    ~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.contrib.sites.models import Site

from pylucid_project.apps.pylucid.models import PageContent


class Search(object):
    def get_queryset(self, request, search_languages, search_strings):
        queryset = PageContent.objects.select_related()

        # search only all pages from this site
        queryset = queryset.filter(pagemeta__pagetree__site=Site.objects.get_current())

        # Filter view permissions:
        # TODO: Check this in unittests!
        if request.user.is_anonymous(): # Anonymous user are in no user group
            queryset = queryset.filter(pagemeta__permitViewGroup=None)
            queryset = queryset.filter(pagemeta__pagetree__permitViewGroup=None)
        elif not request.user.is_superuser: # Superuser can see everything ;)
            user_groups = request.user.groups.all()
            queryset = queryset.filter(pagemeta__permitViewGroup__in=user_groups)
            queryset = queryset.filter(pagemeta__pagetree__permitViewGroup__in=user_groups)

        # Only pages in the selected search language
        queryset = queryset.filter(pagemeta__language__in=search_languages)

        for term in search_strings:
            queryset = queryset.filter(content__icontains=term)
        return queryset

    def add_search_results(self, request, queryset, search_results):
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
                content=page.get_search_content(request),

                # hits in meta content has a higher score, but the content would not displayed 
                meta_content=page.pagemeta.keywords + " " + page.pagemeta.description,
            )
