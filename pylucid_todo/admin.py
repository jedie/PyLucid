# coding: utf-8

"""
    PyLucid ToDo Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib import admin

from pylucid_todo.models import ToDoPlugin


class ToDoPluginAdmin(admin.ModelAdmin):
    list_display = ("id", "code")

admin.site.register(ToDoPlugin, ToDoPluginAdmin)