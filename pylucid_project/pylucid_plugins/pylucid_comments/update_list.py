# coding:utf-8

"""
    Add items to the page update list
"""

from pylucid_comments.models import PyLucidComment

def get_update_list(request, update_list, max_count):
    queryset = PyLucidComment.objects.filter(is_removed=False).order_by('-submit_date')[:max_count]
    for item in queryset:
        update_list.add(
            lastupdatetime=item.submit_date,
            lastupdateby=item.userinfo["name"],
            content_type="blog comment",
            language=item.lang,
            url=item.get_absolute_url(),
            title="blog comment", #item.title_or_slug()
        )

