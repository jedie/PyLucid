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
        if request.GET: # Don't redirect, if any GET parameter in url
            return super(PyLucidAdminSite, self).logout(request)

        url = "/?" + settings.PYLUCID.AUTH_LOGOUT_GET_VIEW
        return HttpResponseRedirect(url)

    def login(self, request):
        """
        redirect to PyLucid's own login view
        """
        if request.GET or PageTree.on_site.all().count() == 0 or UserProfile.on_site.all().count() == 0:
            # Use the normal django login view
            # This must be happend if PyLucid can't work.
            # The User can also "deactivate" the redirect to PyLucid login view by adding any GET parameter
            # e.g: domain.tld/admin/?foobar
            return super(PyLucidAdminSite, self).login(request)

        url = settings.PYLUCID.AUTH_NEXT_URL % {"path": "/", "next_url": request.get_full_path()}
        return HttpResponseRedirect(url)

pylucid_admin_site = PyLucidAdminSite()

# Use all django contrib model admins in our own admin site ;)
pylucid_admin_site._registry = admin.site._registry
