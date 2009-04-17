# coding: utf-8

"""
    dbpreferences.admin
    ~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from dbpreferences.models import Preference

#------------------------------------------------------------------------------

class PreferenceAdmin(admin.ModelAdmin):   
    pass

#    list_display = (
#        "id", "shortcut", "name", "title", "description",
#        "lastupdatetime", "lastupdateby"
#    )
#    list_display_links = ("shortcut",)
#    list_filter = (
#        "createby", "lastupdateby", "permitViewPublic", "showlinks",
#        "template", "style", "markup",
#    )
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ["content", "name", "title", "description", "keywords"]

admin.site.register(Preference, PreferenceAdmin)
