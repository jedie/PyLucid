# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.contrib.admin.sites import AlreadyRegistered
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.conf.urls.defaults import patterns, url, include


from reversion.admin import VersionAdmin

from pylucid.models import PageTree
from pylucid_admin import models


#-----------------------------------------------------------------------------
# some django admin stuff is broken if TEMPLATE_STRING_IF_INVALID != ""
# http://code.djangoproject.com/ticket/3579

if settings.TEMPLATE_STRING_IF_INVALID != "":
    # Patch the render_to_response function ;)
    from django.contrib.auth import admin as auth_admin
    from django.contrib.admin import options

    def patched_render_to_response(*args, **kwargs):
        old = settings.TEMPLATE_STRING_IF_INVALID
        settings.TEMPLATE_STRING_IF_INVALID = ""
        result = render_to_response(*args, **kwargs)
        settings.TEMPLATE_STRING_IF_INVALID = old
        return result

    options.render_to_response = patched_render_to_response
    auth_admin.render_to_response = patched_render_to_response

#------------------------------------------------------------------------------


class PyLucidAdminSite(admin.AdminSite):
    """
    Own PyLucid Admin Site.
    """
    def register(self, *args, **kwargs):
        """ FIXME: Don't know why some models are already registered """
        try:
            super(PyLucidAdminSite, self).register(*args, **kwargs)
        except AlreadyRegistered, err:
            from django_tools.middlewares import ThreadLocal
            request = ThreadLocal.get_current_request()
            if request.META["SERVER_SOFTWARE"].startswith("WSGIServer"):
                import traceback
                print traceback.format_exc()

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

# Use all django contrib model admins in our own admin site ;)
pylucid_admin_site._registry = admin.site._registry

#-----------------------------------------------------------------------------

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin

if settings.DEBUG:
    class PermissionAdmin(admin.ModelAdmin):
        """ django auth Permission """
        list_display = ("id", "name", "content_type", "codename")
        list_display_links = ("name", "codename")
        list_filter = ("content_type",)
    pylucid_admin_site.register(Permission, PermissionAdmin)

    class ContentTypeAdmin(admin.ModelAdmin):
        """ django ContentType """
        list_display = list_display_links = ("id", "app_label", "name", "model")
        list_filter = ("app_label",)
    pylucid_admin_site.register(ContentType, ContentTypeAdmin)


#-----------------------------------------------------------------------------


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
