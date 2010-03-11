# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect


class PyLucidAdminSite(admin.AdminSite):
    """
    Own PyLucid Admin Site.
    """
    def logout(self, request):
        if request.GET: # Don't redirect, if any GET parameter in url
            return super(PyLucidAdminSite, self).logout(request)

        # Use the PyLucid own logout view, so the user it back on his cms page
        url = "/?" + settings.PYLUCID.AUTH_LOGOUT_GET_VIEW
        return HttpResponseRedirect(url)


pylucid_admin_site = PyLucidAdminSite()


# Use all django contrib model admins in our own admin site ;)
pylucid_admin_site._registry = admin.site._registry
