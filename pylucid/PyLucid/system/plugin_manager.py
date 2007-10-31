#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid Plugin Manager
    ~~~~~~~~~~~~~~~~~~~~~~

    The plugin manager starts a plugin an returns the content back.
    For _command requests and for {% lucidTag ... %}

    install/Deintstall plugins into the database.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


import os, sys, cgi, traceback

#~ debug = False
debug = True

from django.conf import settings

#if __name__ == "__main__": # init django for local test
#    from django.core.management import setup_environ
#    setup_environ(settings)

from django.http import HttpResponse

from PyLucid.system.exceptions import *
from PyLucid.models import Plugin, Markup, PagesInternal

def _import(request, from_name, object_name):
    """
    from 'from_name' import 'object_name'
    """
    try:
        return __import__(from_name, {}, {}, [object_name])
    except (ImportError, SyntaxError), e:
        if request.user.is_superuser or request.debug:
            raise
        raise ImportError, "Can't import %s from %s: %s" % (
            object_name, from_name, e
        )

def get_plugin_class(request, package_name, plugin_name):
    """
    import the plugin/plugin and returns the class object
    """
    plugin = _import(request,
        from_name = ".".join([package_name, plugin_name, plugin_name]),
        object_name = plugin_name
    )
    plugin_class = getattr(plugin, plugin_name)
    return plugin_class

def get_plugin_config(request, package_name, plugin_name,
                            dissolve_version_string=False, extra_verbose=False):
    """
    imports the plugin and the config plugin and returns a merge config-object

    dissolve_version_string == True -> get the version string (__version__)
        from the plugin and put it into the config object
    """
    config_name = "%s_cfg" % plugin_name

    def get_plugin(object_name):
        from_name = ".".join([package_name, plugin_name, object_name])
        if extra_verbose:
            print "from %s import %s" % (from_name, object_name)
        return _import(request, from_name, object_name)

    config_plugin = get_plugin(config_name)

    if dissolve_version_string:
        plugin_plugin = get_plugin(plugin_name)

        plugin_version = getattr(plugin_plugin, "__version__", None)
        if plugin_version:
            # Cleanup a SVN Revision Number
            plugin_version = plugin_version.strip("$ ")
        config_plugin.__version__ = plugin_version

    return config_plugin

def _run(context, local_response, plugin_name, method_name, url_args,
                                                                method_kwargs):
    """
    get the plugin and call the method
    """
    request = context["request"]

    def error(msg):
        msg = "Error run plugin/plugin '%s.%s: %s" % (
            plugin_name, method_name, msg
        )
        context["page_msg"](msg)
        msg2 = '<i title="(Error details in page messages.)">["%s.%s" error.]</i>' % (
            plugin_name, method_name
        )
        local_response.write(msg2)

#    context["page_msg"](plugin_name, method_name)
    try:
        plugin = Plugin.objects.get(plugin_name=plugin_name)
    except Plugin.DoesNotExist, e:
        error("Plugin not exists in database: %s" % e)
        return

    plugin_config = get_plugin_config(request,
        package_name = plugin.package_name,
        plugin_name = plugin.plugin_name,
        dissolve_version_string=False
    )
#    context["page_msg"](plugin_config.plugin_manager_data)
    try:
        method_cfg = plugin_config.plugin_manager_data[method_name]
    except KeyError:
        error("Can't get config for the method '%s'." % method_name)
        return

#    context["page_msg"](method_cfg)
    if method_cfg["must_login"]:
        # User must be login to use this method
        # http://www.djangoproject.com/documentation/authentication/

        request.must_login = True # For static_tags an the robot tag

        if request.user.username == "":
            # User is not logged in
            if method_cfg.get("no_rights_error", False) == True:
                # No error message should be displayed for this plugin.
                # e.g. admin_menu
                return ""
            else:
                raise AccessDeny

    URLs = context["URLs"]
    URLs.current_plugin = plugin_name

    plugin_class=get_plugin_class(request, plugin.package_name, plugin_name)
    class_instance = plugin_class(context, local_response)
    unbound_method = getattr(class_instance, method_name)

    output = unbound_method(*url_args, **method_kwargs)

    return output



def run(context, response, plugin_name, method_name, url_args=(),
                                                            method_kwargs={}):
    """
    run the plugin with errorhandling
    """
#    print "plugin_manager.run():", plugin_name, method_name, url_args, method_kwargs
    request = context["request"]
    if request.debug:
        return _run(
            context, response, plugin_name, method_name,
            url_args, method_kwargs
        )
    else:
        try:
            return _run(
                context, response, plugin_name, method_name,
                url_args, method_kwargs
            )
        except Exception:
            msg = "Run plugin %s.%s Error" % (plugin_name, method_name)
            context["page_msg"].red("%s:" % msg)
            import sys, traceback
            context["page_msg"]("<pre>%s</pre>" % traceback.format_exc())
            return msg + "(Look in the page_msg)"


def handle_command(context, response, plugin_name, method_name, url_args):
    """
    handle a _command url request
    """
    output = run(context, response, plugin_name, method_name, url_args)
    return output

#_____________________________________________________________________________
# some routines around plugins/plugins

def file_check(plugin_path, dir_item):
    """
    Test if the given plugin_path/dir_item can be a PyLucid Plugin.
    """
    for item in ("__init__.py", "%s.py", "%s_cfg.py"):
        if "%s" in item:
            item = item % dir_item
        item = os.path.join(plugin_path, dir_item, item)
        if not os.path.isfile(item):
            return False
    return True

def get_plugin_list(plugin_path):
    """
    Return a list with the plugin names for the given path.
    """
    plugin_list = []
    for dir_item in os.listdir(plugin_path):
        abs_path = os.path.join(plugin_path, dir_item)
        if not os.path.isdir(abs_path) or not file_check(plugin_path, dir_item):
            continue
        plugin_list.append(dir_item)
    return plugin_list


def get_internalpage_files(package_name, plugin_name, internal_page_name):
    """
    read html, js, css files for the internal page.
    If there exist no file, it returns "".
    """
    basepath = os.path.join(
        package_name.replace(".",os.sep), plugin_name, "internal_pages",
        internal_page_name,
    )
    def read_file(ext):
        try:
            f = file(basepath + ext, "r")
            content = f.read()
            f.close()
        except IOError, e:
            return ""
        else:
            return content

    html = read_file(".html")
    js = read_file(".js")
    css = read_file(".css")

    return html, js, css


def install_internalpage(plugin, package_name, plugin_name, plugin_config,
                                                                extra_verbose):
    """
    install all internal pages for the given plugin.

    TODO: Befor create: check if page is in db
    """
#    try:
#        internal_page = PagesInternal.objects.get(name = internal_page_name)
#    except PagesInternal.DoesNotExist, e:

    try:
        plugin_manager_data = plugin_config.plugin_manager_data
    except AttributeError:
        # The old way?
        try:
            plugin_manager_data = plugin_config.module_manager_data
        except AttributeError, e:
            msg = (
                "Can't get 'plugin_manager_data' from %s.%s"
                " (Also old 'module_manager_data' not there.)"
                " Org.Error: %s"
            ) % (package_name, plugin_name, e)
            raise AttributeError(msg)
        print "*** DeprecationWarning: ***"
        print " - You should rename module_manager_data to plugin_manager_data"
        print

    for method, cfg in plugin_manager_data.iteritems():
        if not "internal_page_info" in cfg:
            # plugin method has no internal page
            continue

        internal_page_info = cfg["internal_page_info"]

        # complete name:
        internal_page_name = internal_page_info.get("name", method)

        html, js, css = get_internalpage_files(
            package_name, plugin_name, internal_page_name
        )

        markup_name = internal_page_info.get("markup", None)
        if markup_name == None:
            markup_name = "None"
        elif markup_name == "tinyTextile":
            print "*** DeprecationWarning: ***"
            print " - Markup name 'tinyTextile' was renamed to 'textile'!"
            print " - Please correct the config entry."
            markup_name = "textile"

        markup = Markup.objects.get(name=markup_name)

        template_engine = internal_page_info.get("template_engine", None)
        if template_engine:
            print "*** DeprecationWarning: ***"
            print " - 'template_engine' key in internal_page_info is obsolete!"
            print " - Only django template engine is supported!"
            print

        internal_page_name = ".".join([plugin_name, internal_page_name])

        # django bug work-a-round
        # http://groups.google.com/group/django-developers/browse_thread/thread/e1ed7f81e54e724a
        internal_page_name = internal_page_name.replace("_", " ")

        if extra_verbose:
            print "install internal page '%s'..." % internal_page_name,
        internal_page = PagesInternal.objects.create(
            name = internal_page_name,
            plugin = plugin, # The associated plugin
            markup = markup,

            content_html = html,
            content_js = js,
            content_css = css,
            description = internal_page_info['description'],
        )
        if extra_verbose:
            print "OK"

def _install_plugin(package_name, plugin_name, plugin_config, active,
                                                                extra_verbose):
    """
    insert a plugin/plugin in the 'plugin' table
    """
    if extra_verbose:
        print "Install %s.%s..." % (package_name, plugin_name),
    plugin = Plugin.objects.create(
        package_name = package_name,
        plugin_name = plugin_name,
        version = plugin_config.__version__,
        author = plugin_config.__author__,
        url = plugin_config.__url__,
        description = plugin_config.__description__,
        long_description = plugin_config.__long_description__,
        can_deinstall = getattr(plugin_config, "__can_deinstall__", True),
        active = active,
    )
    plugin.save()
    if extra_verbose:
        print "OK, ID:", plugin.id
    return plugin

def install_plugin(request, package_name, plugin_name, active,
                                                        extra_verbose=False):
    """
    Get the config object from disk and insert the plugin into the database
    """
    plugin_config = get_plugin_config(request,
        package_name, plugin_name,
        dissolve_version_string=True, extra_verbose=extra_verbose
    )
    if extra_verbose:
        obsolete_test = (
            hasattr(plugin_config, "__important_buildin__") or
            hasattr(plugin_config, "__essential_buildin__")
        )
        if obsolete_test:
            print "*** DeprecationWarning: ***"
            print (
                " - '__important_buildin__'"
                " or '__essential_buildin__'"
                " are obsolete."
            )

    plugin = _install_plugin(
        package_name, plugin_name, plugin_config, active, extra_verbose
    )
    install_internalpage(
        plugin, package_name, plugin_name, plugin_config, extra_verbose
    )


def auto_install_plugins(request, extra_verbose=True):
    """
    Install all internal plugin how are markt as important or essential.
    """
    Plugin.objects.all().delete()    # delete all installed Plugins

    for path_cfg in settings.PLUGIN_PATH:
        if path_cfg["auto_install"] == True:
            _auto_install_plugins(request, path_cfg, extra_verbose)


def _auto_install_plugins(request, path_cfg, extra_verbose):
    package_name = ".".join(path_cfg["path"])

    plugin_path = os.path.join(*path_cfg["path"])
    plugin_list = get_plugin_list(plugin_path)

    for plugin_name in plugin_list:
        if extra_verbose:
            print "\n\ninstall '%s' plugin: *** %s ***\n" % (
                path_cfg["type"], plugin_name
            )

        try:
            install_plugin(request,
                package_name, plugin_name,
                active=True, extra_verbose=extra_verbose
            )
        except Exception, e:
            print "Error:", e
            continue

        if extra_verbose:
            print "OK, plugins installed."







