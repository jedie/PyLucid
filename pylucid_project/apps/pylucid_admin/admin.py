# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import patterns, url, include
from django.http import HttpResponse, HttpResponseRedirect

from reversion.admin import VersionAdmin

from pylucid.models import PageTree
from pylucid_admin import models


#-----------------------------------------------------------------------------
# add user broken, if TEMPLATE_STRING_IF_INVALID != ""
# http://code.djangoproject.com/ticket/11176
from django.contrib.auth.admin import UserAdmin

org_add_view = UserAdmin.add_view
def ugly_patched_add_view(*args, **kwargs):
    old = settings.TEMPLATE_STRING_IF_INVALID
    settings.TEMPLATE_STRING_IF_INVALID = ""
    result = org_add_view(*args, **kwargs)
    settings.TEMPLATE_STRING_IF_INVALID = old
    return result

UserAdmin.add_view = ugly_patched_add_view


#------------------------------------------------------------------------------


class PyLucidAdminSite(admin.AdminSite):
    """
    Own PyLucid Admin Site.
    """
    def __init__(self, *args, **kwargs):
        super(PyLucidAdminSite, self).__init__(*args, **kwargs)

        # Quick work-a-round for http://code.djangoproject.com/ticket/10061
        self.root_path = "/%s/" % settings.ADMIN_URL_PREFIX

#    def get_urls(self):
#        urls = super(PyLucidAdminSite, self).get_urls()
#        my_urls = patterns('',
#            url(r'/?auth=logout', self.logout, name='%sadmin_logout'),
#            url(r'/?auth=logout', self.logout, name='%sadmin_logout' % self.name),
#        )
#        return my_urls + urls

    def logout(self, request):
        url = "/?" + settings.PYLUCID.AUTH_LOGOUT_GET_VIEW
        return HttpResponseRedirect(url)

    def login(self, request):
        """
        redirect to PyLucid's own login view
        """
        if PageTree.objects.all().count() == 0:
            # FIXME: The PyLucid inline login view does only work after install...
            # Work-a-round: Use the normal django login view
            return super(PyLucidAdminSite, self).login(request)

        url = settings.PYLUCID.AUTH_NEXT_URL % {"path": "/", "next_url": request.get_full_path()}
        return HttpResponseRedirect(url)

pylucid_admin_site = PyLucidAdminSite()



class PyLucidAdminPageAdmin(VersionAdmin):
    list_display = ("id", "name", "title", "url_name", "superuser_only", "access_permissions")
    list_display_links = ("name",)
    list_filter = ("createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name", "title", "url_name")

    def superuser_only(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return superuser_only
    superuser_only.boolean = True

    def access_permissions(self, obj):
        superuser_only, access_permissions = obj.get_permissions()
        return " | ".join(access_permissions)

pylucid_admin_site.register(models.PyLucidAdminPage, PyLucidAdminPageAdmin)
