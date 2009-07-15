# coding:utf-8

from django.core import urlresolvers

from pylucid_admin.models import PyLucidAdminPage

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

    def add_menu_entry(self, name, access_permissions, superuser_only, title, parent, url_name=None):
        if url_name: # verify the url
            url = urlresolvers.reverse(viewname=url_name)

        adminpage_entry, created = PyLucidAdminPage.objects.get_or_create(
            name=name, defaults={
                "title": title, "parent": parent, "url_name": url_name, "superuser_only": superuser_only
            }
        )
        if created:
            self.output.append("PyLucidAdminPage %r created." % adminpage_entry)
        else:
            self.output.append("PyLucidAdminPage %r exist." % adminpage_entry)

        adminpage_entry.add_access_permissions(access_permissions)
        adminpage_entry.save()

        return adminpage_entry


    def get_or_create_section(self, section_name, superuser_only=True):
        title = ADMIN_SECTIONS.get(section_name, section_name)
        adminpage_entry = self.add_menu_entry(
            name=section_name, access_permissions=(), superuser_only=superuser_only,
            title=title, parent=None
        )
        return adminpage_entry
