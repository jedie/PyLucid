# -*- coding: utf-8 -*-

"""
    PyLucid sitemap
    ~~~~~~~~~~~~~~~

    ToDo: Use the Template to generate the Sitemap tree.
    But there is no recuse-Tag in the django template engine :(
    - http://www.python-forum.de/topic-9655.html
    - http://groups.google.com/group/django-users/browse_thread/thread/3bd2812a3d0f7700/14f61279e0e9fd90

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__ = "$Rev$"


from pylucid.models import PageTree, PageMeta, PageContent, Language
from pylucid.decorators import render_to


@render_to("SiteMap/SiteMap.html")
def lucidTag(request):
    """ Create the sitemap tree """
    current_lang = request.PYLUCID.lang_entry

    tree = PageTree.objects.get_tree()

    # insert all PageMeta objects into tree
    queryset = PageMeta.objects.all().filter(lang=current_lang)

    # Filter PageTree view permissions:
    if request.user.is_anonymous(): # Anonymous user are in no user group
        queryset = queryset.filter(page__permitViewGroup=None)
    elif not request.user.is_superuser: # Superuser can see everything ;)
        queryset = queryset.filter(page__permitViewGroup__in=request.user.groups)

    tree.add_related(queryset, field="page", attrname="pagemeta")
    #tree.debug()

    return {"nodes": tree.get_first_nodes()}
