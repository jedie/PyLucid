# coding: utf-8

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    def view_on_site_link(self, obj):
        """ view on site link in admin changelist, try to use complete uri with site info. """
        absolute_url = obj.get_absolute_url()
        if hasattr(obj, "get_absolute_uri"):
            url = obj.get_absolute_uri() # complete uri contains protocol and site domain.
        else:
            url = absolute_url

        context = {"absolute_url": absolute_url, "url": url}
        html = render_to_string('admin/pylucid/includes/view_on_site_link.html', context)
        return html

    view_on_site_link.short_description = _("View on site")
    view_on_site_link.allow_tags = True


class RedirectToPageAdmin(object):
    """
    redirect to the site, after model was added or changed.
    The model object must have get_absolute_url() method!
    """
    def redirect_to_page(self, obj):
        url = obj.get_absolute_url()
        return HttpResponseRedirect(url)

    def response_add(self, request, obj, **kwargs):
        """ goto site after creation """
        response = super(RedirectToPageAdmin, self).response_add(request, obj, **kwargs) # create user message
        if response['Location'] == "../":
            # goto site, if we redirectet to the change list
            response = self.redirect_to_page(obj)
        return response

    def response_change(self, request, obj, **kwargs):
        """ goto site after editing """
        response = super(RedirectToPageAdmin, self).response_change(request, obj, **kwargs) # create user message
        if response['Location'] == "../":
            # goto site, if we redirectet to the change list
            response = self.redirect_to_page(obj)
        return response
