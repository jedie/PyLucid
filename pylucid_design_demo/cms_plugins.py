# coding: utf-8

"""
    PyLucid DesignSwitch Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.http import HttpResponseRedirect

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cms.models import Page
from cms import constants
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool


class DesignSwitchPlugin(CMSPluginBase):
    # model = DesignSwitchPlugin
    name = _("DesignSwitch")
    render_template = "pylucid_design_demo/DesignSwitch.html"

    def render(self, context, instance, placeholder):
        request = context["request"]
        current_page = request.current_page

        context.update({
            "templates": settings.CMS_TEMPLATES,
            "current_page": current_page,
        })
        return context


plugin_pool.register_plugin(DesignSwitchPlugin)
