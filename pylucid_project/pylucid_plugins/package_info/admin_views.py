# coding:utf-8

from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu


def install(request):
    """ insert PyLucid admin views into AdminMenu """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("system")

    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="package_info-used_packages",
        name="package info", title="Liste all used python packages",
    )

    return "\n".join(output)



@check_permissions(superuser_only=False, permissions=())#"blog.add_blogentry",))
@render_to("package_info/admin_package_info.html")
def used_packages(request):
    return {"title": _("package information")}


