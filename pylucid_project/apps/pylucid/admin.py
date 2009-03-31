# coding: utf-8

"""
    PyLucid.admin
    ~~~~~~~~~~~~~~

    Register all PyLucid model in django admin interface.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import admin

from pylucid_project.apps.pylucid.models import PageTree, Language, PageContent


#------------------------------------------------------------------------------

class PageTreeAdmin(admin.ModelAdmin):
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

admin.site.register(PageTree, PageTreeAdmin)


class LanguageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Language, LanguageAdmin)


class PageContentAdmin(admin.ModelAdmin):
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

admin.site.register(PageContent, PageContentAdmin)


