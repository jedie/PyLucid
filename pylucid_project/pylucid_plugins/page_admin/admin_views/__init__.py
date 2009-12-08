# coding: utf-8

from django.conf import settings

from pylucid_project.apps.pylucid.models import PageTree

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_content_page",
        name="new content page", title="Create a new content page.",
        get_pagetree=True
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-new_plugin_page",
        name="new plugin page", title="Create a new plugin page.",
        get_pagetree=True
    )

    menu_section_entry = admin_menu.get_or_create_section("tools")
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="PageAdmin-bulk_editor",
        name="bulk editor", title="Edit one attribute for all model items at once.",
    )

    return "\n".join(output)


def _get_pagetree(request):
    """
    returns the PageTree instance given by ID in GET parameters.
    Used in new_content_page and new_plugin_page.
    """
    raw_pagetree_id = request.GET.get("pagetree")
    if not raw_pagetree_id:
        return

    err_msg = "Wrong PageTree ID."

    try:
        pagetree_id = int(raw_pagetree_id)
    except Exception, err:
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (raw_pagetree_id, err)
        request.page_msg.error(err_msg)
        return

    try:
        parent_pagetree = PageTree.on_site.get(id=pagetree_id)
    except PageTree.DoesNotExist, err:
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (pagetree_id, err)
        request.page_msg.error(err_msg)
        return

    return parent_pagetree


def _build_form_initial(request, parent_pagetree):
    """
    Build a initial dict for preselecting some form fields.
    Used in new_content_page and new_plugin_page.
    """
    initial_data = {}

    info_msg = "preselect some values from %r" % parent_pagetree.get_absolute_url()
    if settings.DEBUG:
        info_msg += " (PageTree: %r)" % parent_pagetree
    request.page_msg.info(info_msg)

    for attr_name in ("design", "showlinks", "permitViewGroup", "permitEditGroup"):
        model_attr = getattr(parent_pagetree, attr_name)
        if hasattr(model_attr, "pk"):
            # XXX: Why must we discover the ID here? A django Bug?
            initial_data[attr_name] = model_attr.pk
        else:
            initial_data[attr_name] = model_attr

    # Create a sub page under the current PageTree
    initial_data["parent"] = parent_pagetree.pk

    return initial_data









