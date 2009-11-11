# coding: utf-8

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect

from pylucid.models import PageTree, UserProfile



class PyLucidAdminSite(admin.AdminSite):
    """
    Own PyLucid Admin Site.
    """
    def logout(self, request):
        url = "/?" + settings.PYLUCID.AUTH_LOGOUT_GET_VIEW
        return HttpResponseRedirect(url)

    def login(self, request):
        """
        redirect to PyLucid's own login view
        """
        if PageTree.on_site.all().count() == 0 or UserProfile.on_site.all().count() == 0:
            # The PyLucid inline login view does only work if e.g. a v0.8 migration starts
            # Work-a-round: Use the normal django login view
            return super(PyLucidAdminSite, self).login(request)

        url = settings.PYLUCID.AUTH_NEXT_URL % {"path": "/", "next_url": request.get_full_path()}
        return HttpResponseRedirect(url)

pylucid_admin_site = PyLucidAdminSite()

# Use all django contrib model admins in our own admin site ;)
pylucid_admin_site._registry = admin.site._registry
