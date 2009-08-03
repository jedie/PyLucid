# coding: utf-8

"""
    Redirect PyLucid Plugin - admin 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Register model in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from pylucid_admin.admin_site import pylucid_admin_site

from redirect.models import RedirectModel


#------------------------------------------------------------------------------

class RedirectModelAdmin(admin.ModelAdmin):
    pass
    #prepopulated_fields = {"slug": ("title",)}    

#    list_display = (
#        "slug", "get_absolute_url", "description",
#        "lastupdatetime", "lastupdateby"
#    )
#    list_display_links = ("slug", "get_absolute_url")
#    list_filter = ("site", "type", "design", "createby", "lastupdateby", )
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ("slug", "description")

pylucid_admin_site.register(RedirectModel, RedirectModelAdmin)
