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

#HTML_TEMPLATE = (
#    '<li>'
#    '    <p class="deep_%(level)s">'
#    '    <a href="%(href)s" title="%(title)s">%(name)s</a> - %(title)s'
#    '    </p>'
#    '</li>'
#)

@render_to("SiteMap/SiteMap.html")
def lucidTag(request):
    """
    Create the sitemap tree
    TODO: We need a real tree here!
    """
    current_lang = request.PYLUCID.lang_entry

    tree = PageTree.objects.get_tree()

    # insert all PageMeta objects into tree
    pagemeta = PageMeta.objects.filter(lang=current_lang)
    tree.add_related(pagemeta, field="page", attrname="pagemeta")

    #tree.debug()
    return {"nodes": tree.get_first_nodes()}

#    languages = Language.objects.all()
#    pages = PageContent.objects.all()
#
#    context = {
#        "languages": languages,
#        "pages": pages,
#    }
#
#    return context


#
#    # Get a tree dict of all pages:
#    sitemap_tree = get_sitemap_tree(self.request)
#
#    # Generate the html page
#    # TODO: This nomaly is the job from the django template engine :(
#    html = self.get_html(sitemap_tree)
#
#    html = mark_safe(html) # turn djngo auto-escaping off
#
#    context = {
#        "sitemap": html,
#    }
#
#    # The CSS data should be added into the CMS page:
#    self._render_template("SiteMap", context)
#
#
#def get_html(menu_data, parent=None):
#    """
#    Generate the html code from the given tree data:
#
#    [{'id': 1L,
#      'level': 1,
#      'name': 'index',
#      'parent': 0L,
#      'shortcut': 'Index',
#      'title': 'index'},
#     {'id': 10L,
#      'level': 1,
#      'name': 'Designs',
#      'parent': 0L,
#      'shortcut': 'Designs',
#      'subitems': [{'id': 13L,
#                    'level': 2,
#                    'name': 'elementary',
#                    'parent': 10L,
#                    'shortcut': 'Elementary',
#                    'title': 'elementary'},
#                   {'id': 12L,
#                    'level': 2,
#                    'name': 'old defaul
#    """
#    result = ["<ul>"]
#
#    for entry in menu_data:
#        href = []
#        if parent:
#            href.append(parent)
#
#        href.append(entry["shortcut"])
#        
#        href = "/".join(href)
#
#        if entry["showlinks"] == True:
#            entry["href"] = self.URLs["absoluteIndex"] + href + "/"
#            result.append(HTML_TEMPLATE % entry)
#
#        if "subitems" in entry:
#            result.append(
#                self.get_html(entry["subitems"], parent=href)
#            )
#
#    result.append("</ul>")
#    return "\n".join(result)
#
#
#
#
#
