# coding: utf-8

"""
    A simple poll plugin
    ~~~~~~~~~~~~~~~~~~~~
    
    Based on django poll tutorial

    :copyleft: 2011-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from poll.models import Poll, Choice, UserVotes, IPVotes


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(CompareVersionAdmin):
    list_display = ("question", "active", "lucidTag_example", "lastupdatetime", "lastupdateby")
    list_display_links = ("question",)
    list_editable = ("active",)
    list_filter = ("active",)
#    fieldsets = [
#        (None, {"fields": ["question"]}),
#        ("permissions", {
#            "fields": ["limit_to_group", "allow_anonymous"],
#        }),
#        ("site information", {"fields": ["sites"]}),
#    ]
    inlines = [ChoiceInline]

    def lucidTag_example(self, obj):
        return '{%% lucidTag poll id=%i %%}' % obj.id
    lucidTag_example.short_description = _("lucidTag example")

admin.site.register(Poll, PollAdmin)

class UserVotesAdmin(admin.ModelAdmin):
    list_display = ("user", "poll")

admin.site.register(UserVotes, UserVotesAdmin)

class IPVotesAdmin(admin.ModelAdmin):
    list_display = ("ip", "count", "poll")

admin.site.register(IPVotes, IPVotesAdmin)
