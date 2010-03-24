# coding:utf-8

from django.core import urlresolvers

from pylucid_project.apps.pylucid_admin.models import PyLucidAdminPage

ADMIN_SECTIONS = {
    "create content": "Create new content."
}


class AdminMenu(object):
    """
    TODO: The section should display a page with a "sub menu" of all sub sections.
    """
    def __init__(self, request, output):
        self.request = request
        self.output = output

#        sys_preferences = SystemPreferencesForm().get_preferences()
#        admin_design_id = sys_preferences["pylucid_admin_design"]
#        self.admin_design = Design.objects.get(id=admin_design_id)

    def add_menu_entry(self, name, title, parent, url_name=None, **extra):
        if url_name: # verify the url
            url = urlresolvers.reverse(viewname=url_name)

        defaults = {"title": title, "parent": parent, "url_name": url_name}
        defaults.update(extra)
        adminpage_entry, created = PyLucidAdminPage.objects.get_or_create(
            name=name, defaults=defaults
        )
        if created:
            self.output.append("PyLucidAdminPage %r created." % adminpage_entry)
        else:
            self.output.append("PyLucidAdminPage %r exist." % adminpage_entry)

        return adminpage_entry

    def get_or_create_section(self, section_name):
        title = ADMIN_SECTIONS.get(section_name, section_name)
        return self.add_menu_entry(section_name, title, parent=None, url_name=None)

