# coding: utf-8


import os
import sys

from django.conf import settings
from django.core import urlresolvers
from django.utils.importlib import import_module
from django.conf.urls.defaults import patterns, url

PYLUCID_PLUGINS = None

_PLUGIN_OBJ_CACHE = {} # cache for PyLucidPlugin.get_plugin_object()
_PLUGIN_URL_CACHE = {} # cache for PyLucidPlugin.get_prefix_urlpatterns()





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
        """ return a object from this plugin """
        mod_pkg = ".".join([self.pkg_string, mod_name])

        cache_key = mod_pkg + obj_name
        if cache_key in _PLUGIN_OBJ_CACHE:
            #print "use _PLUGIN_OBJ_CACHE[%r]" % cache_key
            return _PLUGIN_OBJ_CACHE[cache_key]

        try:
            mod = import_module(mod_pkg)
        except ImportError, err:
            if str(err) == "No module named admin_urls":
                raise self.ObjectNotFound("Can't import %r: %s" % (mod_pkg, err))

            # insert more information into the traceback
            etype, evalue, etb = sys.exc_info()
            evalue = etype('Plugin %r error while importing %r: %s' % (self.name, mod_pkg, evalue))
            raise etype, evalue, etb

        try:
            object = getattr(mod, obj_name)
        except AttributeError, err:
            raise self.ObjectNotFound(err)

        #print "put in _PLUGIN_OBJ_CACHE[%r]" % cache_key
        _PLUGIN_OBJ_CACHE[cache_key] = object

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

        request.plugin_name = None
        request.method_name = None
#        del(request.plugin_name)
#        del(request.method_name)

        return response

    def get_urlpatterns(self, urls_filename):
        """ returns the plugin urlpatterns """
        if "." in urls_filename:
            urls_filename = os.path.splitext(urls_filename)[0]

        raw_plugin_urlpatterns = self.get_plugin_object(mod_name=urls_filename, obj_name="urlpatterns")
        return raw_plugin_urlpatterns


    def get_prefix_urlpatterns(self, url_prefix, urls_filename):
        """ include the plugin urlpatterns with the url prefix """
        if not url_prefix.endswith("/"):
            url_prefix += "/"

        cache_key = self.pkg_string + url_prefix
        if cache_key in _PLUGIN_URL_CACHE:
            #print "use _PLUGIN_URL_CACHE[%r]" % cache_key
            return _PLUGIN_URL_CACHE[cache_key]

        raw_plugin_urlpatterns = self.get_urlpatterns(urls_filename)

        # like django.conf.urls.defaults.include
        plugin_urlpatterns = patterns('', url(url_prefix, [raw_plugin_urlpatterns]))

        #print "put in _PLUGIN_URL_CACHE[%r]" % cache_key
        _PLUGIN_URL_CACHE[cache_key] = plugin_urlpatterns

        return plugin_urlpatterns


    def get_plugin_url_resolver(self, url_prefix, urls_filename="urls"):
        prefix_urlpatterns = self.get_prefix_urlpatterns(url_prefix, urls_filename)

        plugin_url_resolver = urlresolvers.RegexURLResolver(r'^/', prefix_urlpatterns)

        #for key, value in plugin_url_resolver.reverse_dict.items(): print key, value

        return plugin_url_resolver

    def get_merged_url_resolver(self, url_prefix, urls_filename="urls"):
        """ Merge the globale url patterns with the plugin one, so the plugin can reverse all urls """
        prefix_urlpatterns = self.get_prefix_urlpatterns(url_prefix, urls_filename)

        ROOT_URLCONF_PATTERNS = import_module(settings.ROOT_URLCONF).urlpatterns
        merged_urlpatterns = ROOT_URLCONF_PATTERNS + prefix_urlpatterns

        # Make a own url resolver
        merged_url_resolver = urlresolvers.RegexURLResolver(r'^/', merged_urlpatterns)
        return merged_url_resolver




class PyLucidPlugins(dict):
    """ Storage for all existing PyLucid plugins """
    def __init__(self):
        super(PyLucidPlugins, self).__init__()

        self.template_dirs = None # for expand: settings.TEMPLATE_DIRS
        self.pkg_list = None # for expand: settings.INSTALLED_APPS

    def get_admin_urls(self):
        """
        return all existing plugin.admin_urls prefixed with the plugin name.
        Used in apps/pylucid_admin/urls.py
        """
        urls = []
        for plugin_name, plugin_instance in self.iteritems():
            try:
                admin_urls = plugin_instance.get_plugin_object(
                    mod_name="admin_urls", obj_name="urlpatterns"
                )
            except plugin_instance.ObjectNotFound, err:
                continue

            url_prefix = plugin_name + "/"

            # like django.conf.urls.defaults.include, use plugin name as url prefix
            urls += patterns('', url(url_prefix, [admin_urls]))

        return urls

    def add(self, fs_path, pkg_prefix):
        """ Add all plugins in one filesystem path/packages """
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

    def call_get_views(self, request):
        """ call a pylucid plugin "html get view" and return the response. """
        method_name = settings.PYLUCID.HTTP_GET_VIEW_NAME
        for plugin_name in request.GET.keys():
            if plugin_name not in self:
                # get parameter is not a plugin or unknwon plugin
                continue

            plugin_instance = self[plugin_name]
            try:
                response = plugin_instance.call_plugin_view(
                    request, mod_name="views", func_name=method_name, method_kwargs={}
                )
            except plugin_instance.ObjectNotFound, err:
                # plugin or view doesn't exist
                if settings.DEBUG:
                    raise # Give a developer the full traceback page ;)
                else:
                    # ignore the get parameter
                    continue
            except:
                # insert more information into the traceback
                etype, evalue, etb = sys.exc_info()
                evalue = etype('Error rendering plugin view "%s.%s": %s' % (plugin_name, method_name, evalue))
                raise etype, evalue, etb

            return response



def setup_plugins(plugin_package_list):
    global PYLUCID_PLUGINS

    if PYLUCID_PLUGINS == None:
        PYLUCID_PLUGINS = PyLucidPlugins()
        for fs_path, pkg_prefix in plugin_package_list:
            sys.path.insert(0, fs_path)
            PYLUCID_PLUGINS.add(fs_path, pkg_prefix)
        PYLUCID_PLUGINS.init2()



