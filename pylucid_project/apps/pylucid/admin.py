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

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.models import PageTree, Language, PageContent, Design, EditableHtmlHeadFile


#------------------------------------------------------------------------------

class PageTreeAdmin(VersionAdmin):
    #prepopulated_fields = {"slug": ("title",)}    
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


class LanguageAdmin(VersionAdmin):
    pass

admin.site.register(Language, LanguageAdmin)


class PageContentAdmin(VersionAdmin):
    list_display = ("get_absolute_url", "title_or_slug", "description", "lastupdatetime", "lastupdateby",)
    list_display_links = ("title_or_slug",)
    list_filter = ("keywords", "markup", "createby", "lastupdateby",)
#    date_hierarchy = 'lastupdatetime'
#    search_fields = ["content", "name", "title", "description", "keywords"]

admin.site.register(PageContent, PageContentAdmin)


class DesignAdmin(VersionAdmin):
    pass

admin.site.register(Design, DesignAdmin)


class EditableHtmlHeadFileAdmin(VersionAdmin):
    pass

admin.site.register(EditableHtmlHeadFile, EditableHtmlHeadFileAdmin)