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
    user = request.user
    current_lang = request.PYLUCID.lang_entry

    # Get a pylucid.tree_model.TreeGenerator instance with all accessible PageTree for the current user
    tree = PageTree.objects.get_tree(user, filter_showlinks=True)

    # add all related PageMeta objects into tree
    queryset = PageMeta.objects.filter(lang=current_lang)
    tree.add_related(queryset, field="page", attrname="pagemeta")

    #tree.debug()

    return {"nodes": tree.get_first_nodes()}
