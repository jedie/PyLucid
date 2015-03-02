# coding: utf-8

"""
    PyLucid DesignSwitch Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from cms import constants

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool


class DesignSwitchPlugin(CMSPluginBase):
    # model = DesignSwitchPlugin
    name = _("DesignSwitch")
    render_template = "pylucid_design_demo/DesignSwitch.html"

    cache=None

    def _get_template_page(self, current_page):
        if current_page.template:
            if current_page.template != constants.TEMPLATE_INHERITANCE_MAGIC:
                return current_page
            else:
                print(current_page.get_ancestors(ascending=True))

                print(current_page.get_ancestors(ascending=True).exclude(
                        template=constants.TEMPLATE_INHERITANCE_MAGIC))
                try:
                    return current_page.get_ancestors(ascending=True).exclude(
                        template=constants.TEMPLATE_INHERITANCE_MAGIC)[0]
                except IndexError:
                    pass

    def render(self, context, instance, placeholder):
        # # print(context)
        # print(type(instance))
        # print(placeholder)
        #
        # print(context["CMS_TEMPLATE"])
        #
        # request = context["request"]
        # current_page = request.current_page
        # current_template = request.GET.get("template", current_page.get_template())
        # print(current_template)

        context.update({
            "templates": settings.CMS_TEMPLATES,
            # "current_template": current_template,
        })
        return context


plugin_pool.register_plugin(DesignSwitchPlugin)
