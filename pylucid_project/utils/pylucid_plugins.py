# coding: utf-8

import os
import sys

from django.core import urlresolvers
from django.utils.importlib import import_module

PLUGINS = None





class PyLucidPlugin(object):
    """ represents one PyLucid plugins """

    class ObjectNotFound(Exception):
        """ Can't import a plugin modul or a modul Attribute doesn't exist. """
        pass

    def __init__(self, fs_path, pkg_prefix, plugin_name):
        self.fs_path = fs_path
        self.pkg_string = ".".join([pkg_prefix, plugin_name])
        self.name = plugin_name

        self._template_path = os.path.join(fs_path, "templates")

    def get_template_path(self):
        """ return template filesystem path, if templates exist else: return None """
        if os.path.isdir(self._template_path):
            return self._template_path
        else:
            return None

    def get_plugin_object(self, mod_name, obj_name):
        pkg = ".".join([self.pkg_string, mod_name])
        try:
            mod = import_module(pkg)
        except ImportError, err:
            raise self.ObjectNotFound("Can't import %r: %s" % (pkg, err))

        try:
            object = getattr(mod, obj_name)
        except AttributeError, err:
            raise self.ObjectNotFound(err)

        return object

    def get_callable(self, mod_name, func_name):
        """ returns the callable function. """
        callable = self.get_plugin_object(mod_name, obj_name=func_name)
        return callable

    def call_plugin_view(self, request, mod_name, func_name, method_kwargs):
        """ Call a plugin view """
        callable = self.get_callable(mod_name, func_name)

        # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
        request.plugin_name = self.name
        request.method_name = func_name

        # call the plugin view method
        response = callable(request, **method_kwargs)

        del(request.plugin_name)
        del(request.method_name)

        return response


class PyLucidPlugins(dict):
    """ Storage for all existing PyLucid plugins """
    def __init__(self):
        super(PyLucidPlugins, self).__init__()

        self.template_dirs = None # for expand: settings.TEMPLATE.DIRS
        self.pkg_list = None # for expand: settings.INSTALLED_APPS

    def get_admin_urls(self):
        """
        return all existing plugin.admin_urls
        Used in apps/pylucid_admin/urls.py
        """
        urls = None
        for plugin_name, plugin_instance in self.iteritems():
            try:
                admin_urls = plugin_instance.get_plugin_object(
                    mod_name="admin_urls", obj_name="urlpatterns"
                )
            except plugin_instance.ObjectNotFound, err:
                continue

            if urls == None:
                urls = admin_urls
            else:
                urls += admin_urls

        return urls

    def add(self, fs_path, pkg_prefix):
        """ All all plugins in one filesystem path/packages """
        for plugin_name in os.listdir(fs_path):
            if plugin_name.startswith("."):
                continue
            item_path = os.path.join(fs_path, plugin_name)
            if not os.path.isdir(item_path):
                continue

            if plugin_name in self:
                warnings.warn("Plugin %r exist more than one time." % plugin_name)

            dict.__setitem__(self, plugin_name, PyLucidPlugin(fs_path, pkg_prefix, plugin_name))

    def _get_template_dirs(self):
        """ setup self.template_dirs: append all existing plugin template filesystem path """
        template_dirs = []
        for plugin_name, plugin_instance in self.iteritems():
            template_path = plugin_instance.get_template_path()
            if template_path:
                template_dirs.append(template_path)
        return tuple(template_dirs)

    def init2(self):
        if len(self) == 0:
            raise RuntimeError("init2 must be called after all self.add() calls!")

        self.template_dirs = self._get_template_dirs()
        self.pkg_list = tuple([plugin.pkg_string for plugin in self.values()])



def setup_plugins(plugin_package_list):
    global PLUGINS

    if PLUGINS == None:
        PLUGINS = PyLucidPlugins()
        for fs_path, pkg_prefix in plugin_package_list:
            sys.path.insert(0, fs_path)
            PLUGINS.add(fs_path, pkg_prefix)
        PLUGINS.init2()



