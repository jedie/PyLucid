#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Admin

Einrichten/Konfigurieren von Modulen und Plugins


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev$"

import os

from django.utils.translation import ugettext as _
from django import newforms as forms
from django.conf import settings

from PyLucid.system.plugin_manager import get_plugin_list, install_plugin
from PyLucid.system.plugin_import import get_plugin_config, get_plugin_version
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Plugin


class InstallForm(forms.Form):
    """
    Validate 'install plugin' POST.
    e.g.:
    {
        u'install': [u'install'],
        u'package_name': [u'PyLucid.plugins_external'],
        u'plugin_name': [u'HelloWorld1']
    }
    """
    package_name = forms.CharField(min_length=3, max_length=50)
    plugin_name = forms.CharField(min_length=3, max_length=50)


class ID_Form(forms.Form):
    """
    Validate 'deinstall plugin', 'deactivate plugin' and 'reinit' POST.
    e.g.:
    {u'id': [u'99'], u'deinstall': [u'deinstall']}
    {u'id': [u'99'], u'deactivate': [u'deactivate']}
    {u'id': [u'99'], u'activate': [u'activate']}
    """
    id = forms.IntegerField()


class plugin_admin(PyLucidBasePlugin):

    def menu(self):
        """
        Run the method from a POST and display the menu.
        """
        # Change the global page title:
        self.context["PAGE"].title = _("plugin administration")

        if self.request.method == 'POST':
            POST = self.request.POST
            if "install" in POST:
                form = InstallForm(POST)
                if form.is_valid():
                    plugin_name = form.cleaned_data["plugin_name"]
                    package_name = form.cleaned_data["package_name"]
                    self._install_plugin(plugin_name, package_name)
            else:
                form = ID_Form(POST)
                if form.is_valid():
                    plugin_id = form.cleaned_data["id"]
                    try:
                        if "deinstall" in POST:
                            self._deinstall_plugin(plugin_id)
                        elif "deactivate" in POST:
                            self._deactivate_plugin(plugin_id)
                        elif "activate" in POST:
                            self._activate_plugin(plugin_id)
                        elif "reinit" in POST:
                            self._reinit_plugin(plugin_id)
                    except ActionError, e:
                        self.page_msg.red(e)

        # Build the Menu data and render the Template:

        installed_names = []
        active_plugins = []
        deactive_plugins = []
        installed_plugins = Plugin.objects.all().order_by(
            'package_name', 'plugin_name'
        )
        for plugin in installed_plugins:
            installed_names.append(plugin.plugin_name)
            if plugin.active:
                active_plugins.append(plugin)
            else:
                deactive_plugins.append(plugin)

        uninstalled_plugins = self._get_uninstalled_plugins(installed_names)

        context = {
            "active_plugins": active_plugins,
            "deactive_plugins": deactive_plugins,
            "uninstalled_plugins": uninstalled_plugins,
            "action_url": "#", # FIXME
        }
        self._render_template("administation_menu", context)#, debug=True)

    def _get_uninstalled_plugins(self, installed_names):
        """
        Read all Plugin names from the disk and crop it with the given list.
        """
        uninstalled_plugins = []

        for path_cfg in settings.PLUGIN_PATH:
            package_name = ".".join(path_cfg["path"])

            plugin_path = os.path.join(*path_cfg["path"])
            plugin_list = get_plugin_list(plugin_path)

            for plugin_name in plugin_list:
                if plugin_name in installed_names:
                    continue

                try:
                    plugin_cfg = get_plugin_config(package_name, plugin_name)
                except Exception, err:
                    if self.request.debug:
                        raise
                    msg = "Can't get plugin config for %s.%s, Error: %s" % (
                        package_name, plugin_name, err
                    )
                    self.page_msg(msg)
                    continue

                try:
                    plugin_version = get_plugin_version(
                        package_name, plugin_name
                    )
                except Exception, err:
                    plugin_version = (
                        "Can't get plugin version for %s.%s, Error: %s"
                    ) % (package_name, plugin_name, err)

                uninstalled_plugins.append({
                    "plugin_name": plugin_name,
                    "package_name": package_name,
                    "description": plugin_cfg.__description__,
                    "url": plugin_cfg.__url__,
                    "author": plugin_cfg.__author__,
                    "version": plugin_version,
                })

        return uninstalled_plugins

    def plugin_setup(self):
        self.page_msg("Not implemented yet.")

    #__________________________________________________________________________
    # The real action methods

    def _install_plugin(self, plugin_name, package_name, active=False):
        """
        Put the plugin data and the internal pages from it into the database.
        """
        self.page_msg(_("Install plugin '%s':") % plugin_name)

        if self.request.debug:
            verbosity = 2
        else:
            verbosity = 1

        try:
            install_plugin(
                package_name, plugin_name, self.page_msg, verbosity, active
            )
        except Exception, e:
            if self.request.debug:
                raise
            raise ActionError(_("Error installing Plugin:"), e)
        else:
            self.page_msg.green(
                _("Plugin '%s' saved into the database.") % plugin_name
            )

    def _deinstall_plugin(self, plugin_id, force=False):
        """
        remove internal_pages and the plugin entry from the database.
        """
        if self.request.debug:
            verbosity = 2
        else:
            verbosity = 1
        try:
            plugin = Plugin.objects.get(id=plugin_id)
            if plugin.can_deinstall==False and force==False:
                self.page_msg.red("Can't deinstall the plugin. It's locked.")
                return
            plugin.delete(self.page_msg, verbosity)
        except Exception, e:
            if self.request.debug:
                raise
            raise ActionError(_("Error removing Plugin: %s") % e)
        else:
            self.page_msg.green(
                _("Plugin '%s' removed from the database.") % plugin
            )

    def _deactivate_plugin(self, plugin_id):
        """
        Set the database active flag to False.
        """
        try:
            plugin = Plugin.objects.get(id=plugin_id)
            if plugin.can_deinstall==False:
                self.page_msg.red("Can't deactivate the plugin. It's locked.")
                return
            plugin.active = False
            plugin.save()
        except Exception, e:
            if self.request.debug:
                raise
            raise ActionError(_("Can't deactivate Plugin: %s") % e)
        else:
            self.page_msg.green(
                _("Plugin '%s' deactivated.") % plugin.plugin_name
            )

    def _activate_plugin(self, plugin_id):
        """
        Set the database active flag to True.
        """
        try:
            plugin = Plugin.objects.get(id=plugin_id)
            plugin.active = True
            plugin.save()
        except Exception, e:
            if self.request.debug:
                raise
            raise ActionError(_("Can't activate Plugin: %s") % e)
        else:
            self.page_msg.green(
                _("Plugin '%s' activated.") % plugin.plugin_name
            )

    def _reinit_plugin(self, plugin_id):
        """
        Deinstall a plugin, after this install it again and activate it.
        """
        try:
            plugin = Plugin.objects.get(id=plugin_id)
        except Plugin.DoesNotExist:
            self.page_msg.red("Wrong ID")
            return

        plugin_name = plugin.plugin_name
        package_name = plugin.package_name

        try:
            self._deinstall_plugin(plugin_id, force=True)
            self._install_plugin(plugin_name, package_name, active=True)
        except Exception, e:
            if self.request.debug:
                raise
            raise ActionError(_("Can't reinit plugin: %s") % e)
        else:
            self.page_msg.green(_("Reinit complete."))


class ActionError(Exception):
    """
    Appears if any action (de)install/(de)activate fails.
    """
    pass

