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

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from redirect.models import RedirectModel


#------------------------------------------------------------------------------

class RedirectModelAdmin(BaseAdmin):
    list_display = (
        "view_on_site_link", "destination_url", "response_type", "full_url", "append_query_string",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("destination_url", "response_type")
    list_filter = ("response_type", "full_url", "append_query_string", "createby", "lastupdateby",)
    date_hierarchy = 'lastupdatetime'
    search_fields = ("destination_url",)

admin.site.register(RedirectModel, RedirectModelAdmin)
