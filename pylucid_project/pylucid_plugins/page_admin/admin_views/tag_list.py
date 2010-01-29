# coding:utf-8

"""
    PyLucid tag list
    ~~~~~~~~~~~~~~~~
    
    List all available lucidTag
"""

import inspect

from django.template import RequestContext
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.markup.django_tags import DjangoTagAssembler
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to


from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS
from pylucid_project.apps.pylucid.models import PageTree, PageMeta
from pylucid_project.utils.escape import escape




@render_to("page_admin/tag_list_popup.html")
@check_permissions(superuser_only=False,
    permissions=('pylucid.change_pagecontent', 'pylucid.change_pagemeta')
)
def tag_list(request):
    """ Create a list of all existing lucidTag plugin views. """
    lucid_tags = []
    for plugin_name, plugin_instance in PYLUCID_PLUGINS.iteritems():
        try:
            lucidtag_view = plugin_instance.get_plugin_object(
                mod_name="views", obj_name="lucidTag"
            )
        except plugin_instance.ObjectNotFound, err:
            continue

        lucidtag_doc = None
        examples = None
        fallback_example = None

        if lucidtag_view.__name__ == "wrapper":
            request.page_msg(
                _("Info: lucidTag %s used a decorator without functools.wraps!") % plugin_name
            )
        else:
            lucidtag_doc = inspect.getdoc(lucidtag_view)
            if lucidtag_doc: # Cutout lucidTag examples from DocString
                assembler = DjangoTagAssembler()
                _, cut_data = assembler.cut_out(lucidtag_doc)
                examples = cut_data

                for example in examples:
                    if not example.startswith("{%% lucidTag %s " % plugin_name):
                        request.page_msg(
                            _("Info: lucidTag %(plugin_name)s has wrong tag example: %(example)r") % {
                                "plugin_name": plugin_name, "example": example
                            }
                        )

                lucidtag_doc = lucidtag_doc.split("example:", 1)[0].strip()

                # Escape "&", "<", ">" and django template tags chars like "{" and "}"
                lucidtag_doc = escape(lucidtag_doc)

        if not examples:
            # No DocString or it contains no examples -> generate a example
            fallback_example = escape("{%% lucidTag %s %%}" % plugin_name)


        lucid_tags.append({
            "plugin_name": plugin_name.replace("_", " "),
            "fallback_example": fallback_example,
            "examples": examples,
            "doc": lucidtag_doc,
        })

    # Sort by plugin name case-insensitive
    lucid_tags.sort(cmp=lambda x, y: cmp(x["plugin_name"].lower(), y["plugin_name"].lower()))


    # Add PageTree and PageMeta instance to request.PYLUCID for get
    # context keys witch are related to these objects.
    # see pylucid_project.apps.pylucid.context_processors
    old_pylucid_obj = request.PYLUCID

    pagetree = PageTree.objects.get_root_page(request.user)
    pagemeta = PageTree.objects.get_pagemeta(request, pagetree, show_lang_errors=False)
    request.PYLUCID.pagetree = pagetree
    request.PYLUCID.pagemeta = pagemeta

    request_context = RequestContext(request)

    request.PYLUCID = old_pylucid_obj

    # Collect all existing tags from all context dicts
    request_context_dicts = request_context.dicts
    context_keys = set()
    for d in request_context_dicts:
        context_keys.update(set(d.keys()))

    context_keys = list(context_keys)
    context_keys.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))

    context = {
        "title": "lucidTag list",
        "context_keys": context_keys,
        "lucid_tags": lucid_tags
    }
    return context


