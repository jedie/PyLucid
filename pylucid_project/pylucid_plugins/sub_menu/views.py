# -*- coding: utf-8 -*-

"""
    PyLucid sub_menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a link list of all sub pages.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2005-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev$"


from pylucid_project.apps.pylucid.models import PageTree, PageMeta, Language
from pylucid_project.apps.pylucid.decorators import render_to


@render_to("sub_menu/sub_menu.html")
def lucidTag(request):
    """ build the sub menu with all existing sub pages"""
    pagetree = request.PYLUCID.pagetree # current models.PageContent instance
    current_lang = request.PYLUCID.current_language # Client prefered language
    default_lang = Language.objects.get_or_create_default(request) # System default language

    # Build a PageTree ID list of all accessible subpages
    queryset = PageTree.objects.all_accessible(request.user, filter_showlinks=True)
    queryset = queryset.filter(parent=pagetree)
    sub_pagetree_ids = queryset.values_list("id", flat=True)

    # Get PageMeta in client prefered language
    queryset = PageMeta.objects.filter(language=current_lang)
    pagemeta1 = queryset.filter(pagetree__in=sub_pagetree_ids).select_related()
    existing_pagetree1 = [pagemeta.pagetree.id for pagemeta in pagemeta1]

    # Build a list of all PageTree IDs witch haven't a PageMeta
    missing_pagetree1 = [id for id in sub_pagetree_ids if id not in existing_pagetree1]
    if not missing_pagetree1:
        # No missing languages -> Use the source queryset
        sub_pages = list(pagemeta1)
    else: # Some pages didn't exist in current language -> use system default language
        queryset = PageMeta.objects.filter(language=default_lang)
        pagemeta2 = queryset.filter(pagetree__in=missing_pagetree1).select_related()

        # PageMeta in current language + PageMeta in system default language
        sub_pages = list(pagemeta1) + list(pagemeta2)

        # Build a list of existing PageMeta
        existing_pagetree2 = [pagemeta.pagetree.id for pagemeta in sub_pages]
        # Exist there pages not in Client prefered language and not in System default language?
        missing_pagetree2 = [id for id in sub_pagetree_ids if id not in existing_pagetree2]
        if missing_pagetree2: # There are still missing PageMeta.
            queryset = PageMeta.objects.exclude(language=current_lang).exclude(language=default_lang)
            sub_pages3 = queryset.filter(pagetree__in=missing_pagetree2).select_related()

            # merge sub pages
            sub_pages += list(sub_pages3)

    # sort by PageTree positions 
    sub_pages.sort(cmp=lambda x, y: cmp(x.pagetree.position, y.pagetree.position))

    return {"sub_pages": sub_pages}











