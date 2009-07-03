
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from pylucid.models import PyLucidAdminPage, Design
from pylucid.preference_forms import SystemPreferencesForm
from django.contrib.sites.models import Site

ADMIN_SECTIONS = {
    "create content": "Create new content."
}


class AdminMenu(object):
    def __init__(self, request, output):
        self.request = request
        self.output = output

        sys_preferences = SystemPreferencesForm().get_preferences()
        admin_design_id = sys_preferences["pylucid_admin_design"]
        self.admin_design = Design.objects.get(id=admin_design_id)

    def add_menu_entry(self, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = kwargs["name"].replace(" ", "_")

        adminpage_entry, created = PyLucidAdminPage.objects.get_or_create(**kwargs)
        if created:
            self.output.append("PyLucidAdminPage %r created." % adminpage_entry)
        else:
            self.output.append("PyLucidAdminPage %r exist." % adminpage_entry)

        return adminpage_entry


    def get_or_create_section(self, section_name):
        title = ADMIN_SECTIONS[section_name]
        adminpage_entry = self.add_menu_entry(name=section_name, title=title, parent=None)
        return adminpage_entry


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new content page", title="Create a new content page.",
        plugin_name=request.plugin_name,
        view_name="new_content_page",
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new plugin page", title="Create a new plugin page.",
        plugin_name=request.plugin_name,
        view_name="new_plugin_page",
    )

    return "\n".join(output)


def new_content_page(request):
    return """ Create a new page """

def new_plugin_page(request):
    return """ Create a new plugin page """

