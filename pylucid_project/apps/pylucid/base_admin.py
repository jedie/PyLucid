# coding: utf-8

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
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
