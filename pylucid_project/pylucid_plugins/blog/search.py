# coding:utf-8

"""
    search Blog entries
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


from django.db.models import Q

from pylucid_project.pylucid_plugins.blog.models import BlogEntryContent
from pylucid_project.apps.pylucid.models.pluginpage import PluginPage
from pylucid_project.system.pylucid_plugins import PluginNotOnSite


class Search(object):
    def __init__(self):
        queryset = PluginPage.objects.queryset_by_plugin_name("blog")
        if not queryset.exists():
            raise PluginNotOnSite("blog not used on current site!")

    def get_queryset(self, request, search_languages, search_strings):
        queryset = BlogEntryContent.objects.get_prefiltered_queryset(request, tags=None, filter_language=False)

        # Only items in the selected search language
        queryset = queryset.filter(language__in=search_languages)

        queryset = queryset.select_related()

        for term in search_strings:
            queryset = queryset.filter(
                Q(content__icontains=term) | Q(tags__icontains=term) | Q(headline__icontains=term)
            )

        return queryset

    def add_search_results(self, request, queryset, search_results):
    #    plugin_url_resolver = PluginPage.objects.get_url_resolver("blog")

        for item in queryset:
            meta_content = item.tags
            #print "meta: %r" % meta_content

    #        reverse_kwargs = {
    #            "year": item.url_date.year,
    #            "month": "%02i" % item.url_date.month,
    #            "day": "%02i" % item.url_date.day,
    #            "slug": item.slug
    #        }
    #
    #        url = plugin_url_resolver.reverse("Blog-detail_view", kwargs=reverse_kwargs)

            search_results.add(
                model_instance=item,

                # displayed headline of the result hit
                headline=item.headline,

                # displayed in the result list
                language=item.language,

                # Link to the hit
                url=item.get_absolute_url(),
    #            url=url,

                # the main content -> result lines would be cut out from hits in this content
                content=item.get_search_content(request),

                # hits in meta content has a higher score, but the content would not displayed 
                meta_content=meta_content,
            )
