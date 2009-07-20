# coding:utf-8

"""
    Add items to the page update list
"""

from pylucid.models import PageContent

def get_update_list(request, update_list, max_count):
    queryset = PageContent.objects.order_by('-lastupdatetime')[:max_count]
    for item in queryset:
        update_list.add(
            lastupdatetime=item.lastupdatetime,
            lastupdateby=item.lastupdateby,
            content_type="page",
            language=item.lang,
            url=item.get_absolute_url(),
            title=item.title_or_slug()
        )

