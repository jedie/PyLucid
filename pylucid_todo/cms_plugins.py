# coding: utf-8

"""
    PyLucid ToDo Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from pylucid_todo.models import ToDoPlugin


class ToDoPlugin(CMSPluginBase):
    model = ToDoPlugin
    name = _("ToDo")
    render_template = "pylucid_todo/todo.html"

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance
        })
        return context

plugin_pool.register_plugin(ToDoPlugin)
