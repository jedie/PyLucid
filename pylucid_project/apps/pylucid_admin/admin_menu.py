# coding:utf-8

from django.core import urlresolvers

from pylucid.models import PyLucidAdminPage

ADMIN_SECTIONS = {
    "create content": "Create new content."
}


class AdminMenu(object):
    def __init__(self, request, output):
        self.request = request
        self.output = output

#        sys_preferences = SystemPreferencesForm().get_preferences()
#        admin_design_id = sys_preferences["pylucid_admin_design"]
#        self.admin_design = Design.objects.get(id=admin_design_id)

    def add_menu_entry(self, **kwargs):
        if "url_name" in kwargs:
            url_name = kwargs.pop("url_name")
            url = urlresolvers.reverse(viewname=url_name)
            kwargs["url"] = url

        adminpage_entry, created = PyLucidAdminPage.objects.get_or_create(**kwargs)
        if created:
            self.output.append("PyLucidAdminPage %r created." % adminpage_entry)
        else:
            self.output.append("PyLucidAdminPage %r exist." % adminpage_entry)

        return adminpage_entry


    def get_or_create_section(self, section_name):
        title = ADMIN_SECTIONS.get(section_name, section_name)
        adminpage_entry = self.add_menu_entry(name=section_name, title=title, parent=None)
        return adminpage_entry
