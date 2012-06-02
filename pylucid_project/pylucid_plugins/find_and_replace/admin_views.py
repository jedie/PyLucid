# coding: utf-8

"""
    PyLucid find&replace
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

"""
    PyLucid find&replace plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.models.language import Language
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from find_and_replace.forms import FindReplaceForm, CONTENT_TYPES_DICT, CONTENT_TYPES


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("change content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="FindAndReplace-find_and_replace",
        name="find and replace", title="Find and replace in all existing page content",
    )

    return "\n".join(output)


def _do_find_and_replace(request, context, find_string, replace_string, content_type, simulate, languages, sites):
    content_type_no = int(content_type)
    model_name = CONTENT_TYPES[content_type_no][0]
    model = CONTENT_TYPES_DICT[content_type_no]

    search_languages = Language.objects.filter(code__in=languages)

    queryset = model.objects.all()
    messages.info(request,
        _("%(count)s %(model_name)s entries total exist.") % {
            "count": queryset.count(),
            "model_name": model_name,
    })

    if model_name == u"PageContent":
        queryset = queryset.filter(pagemeta__language__in=search_languages)
        queryset = queryset.filter(pagemeta__pagetree__site__in=sites)
    elif model_name == u"BlogEntryContent":
        queryset = queryset.filter(entry__sites__in=sites)
    elif model_name == u"EditableHtmlHeadFile":
        context["no_link"] = True
    else:
        queryset = queryset.filter(sites__in=sites)

    if model_name not in (u"PageContent", u"EditableHtmlHeadFile", u"DBTemplate"):
        queryset = queryset.filter(language__in=search_languages)

    filtered_count = queryset.count()
    messages.info(request,
        _("%(count)s %(model_name)s filtered entries found.") % {
            "count": filtered_count,
            "model_name": model_name,
    })
    if filtered_count == 0:
        return

    queryset = queryset.filter(content__contains=find_string)
    messages.info(request,
        _("%(count)s %(model_name)s entries contains 'find string'.") % {
            "count": queryset.count(),
            "model_name": model_name,
    })

    total_changes = 0
    changed_entry_count = 0
    results = []
    changed_entrys = []
    for entry in queryset:
        old_content = entry.content

        changes = old_content.count(find_string)
        if changes == 0:
            continue

        changed_entry_count += 1
        total_changes += changes

        new_content = old_content.replace(find_string, replace_string)
        if not simulate:
            # Save the find/replace result
            entry.content = new_content
            entry.save()
            changed_entrys.append(entry)

        diff_html = hightlighter.get_pygmentize_diff(old_content, new_content)

        results.append({
            "entry": entry,
            "changes": changes,
            "diff_html": diff_html,
        })

    if total_changes > 0:
        messages.info(request,
            _("%(changes)s changes in %(count)s %(model_name)s entries.") % {
                "changes": total_changes,
                "count": changed_entry_count,
                "model_name": model_name,
        })
        if simulate:
            messages.info(request, "Simulate only, no entry changed.")

    context["results"] = results
    context["changed_entry_count"] = changed_entry_count
    context["total_changes"] = total_changes


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagecontent",))
@render_to("find_and_replace/find_and_replace.html")
def find_and_replace(request):
    """ find and replace a string in all page content. """
    context = {
        "title": _("Find and replace"),
        "form_url": request.path,
    }

    if request.method == "POST":
        form = FindReplaceForm(request.POST)
        if form.is_valid():
            start_time = time.time()
            _do_find_and_replace(request, context, **form.cleaned_data)
            context["duration"] = time.time() - start_time
    else:
        form = FindReplaceForm()

    context["form"] = form
    return context

