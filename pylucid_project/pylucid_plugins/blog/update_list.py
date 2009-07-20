# coding:utf-8

"""
    Add items to the page update list
"""

from blog.models import BlogEntry

def get_update_list(request, update_list, max_count):
    queryset = BlogEntry.objects.order_by('-lastupdatetime')[:max_count]
    for item in queryset:
        update_list.add(
            lastupdatetime=item.lastupdatetime,
            lastupdateby=item.lastupdateby,
            content_type="blog entry",
            language=item.lang,
            url=item.get_absolute_url(),
            title=item.headline
        )

