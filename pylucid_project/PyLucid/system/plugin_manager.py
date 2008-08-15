# -*- coding: utf-8 -*-
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

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os, sys, cgi, traceback

#~ debug = False
debug = True

from django.conf import settings

#from django.db.models import Model
from django.core.management import sql
from django.db import connection, transaction
from django.utils.safestring import mark_safe
from django.http import Http404#, HttpResponse
from django.utils.translation import ugettext as _
from django.core.management.color import no_style

from PyLucid.models import Plugin
from PyLucid.system.exceptions import *
from PyLucid.system.plugin_import import get_plugin_module, \
                                        get_plugin_config, get_plugin_version


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
        request.page_msg(msg)
        msg2 = (
            '<i title="(Error details in page messages.)">["%s.%s" error.]</i>'
        ) % (plugin_name, method_name)
        local_response.write(msg2)

#    request.page_msg(plugin_name, method_name)
    try:
        plugin = Plugin.objects.get(plugin_name=plugin_name)
    except Plugin.DoesNotExist, e:
        if request.debug: # don't use errorhandling -> raise the prior error
            raise
        error("Plugin not exists in database: %s" % e)
        return

    plugin_config = get_plugin_config(plugin.package_name, plugin.plugin_name)
#    request.page_msg(plugin_config.plugin_manager_data)
    try:
        method_cfg = plugin_config.plugin_manager_data[method_name]
    except KeyError:
        if request.debug: # don't use errorhandling -> raise the prior error
            raise
        error("Can't get config for the method '%s'." % method_name)
        return

#    request.page_msg(method_cfg)
    if method_cfg["must_login"]:
        # User must be login to use this method
        # http://www.djangoproject.com/documentation/authentication/
        if request.user.is_anonymous():
            # User is not logged in
            if method_cfg.get("no_rights_error", False) == True:
                # TODO: remove in v0.9, see: ticket:161
                # No error message should be displayed for this plugin.
                # e.g. admin_menu
                return ""
            else:
                raise AccessDenied

    if method_cfg["must_admin"]:
        # The User must be an admin to use this method
        if not (request.user.is_superuser or request.user.is_staff):
            raise AccessDenied

    # set if the current request was viewable for anonymous user
    # interesting for: <meta name="robots" content="{{ robots }}" />
    if request.anonymous_view == True:
        # Only change anonymous_view, if it not set to False in the past.
        if method_cfg["must_login"] or method_cfg["must_admin"]:
            request.anonymous_view = False

    URLs = context["URLs"]
    URLs.current_plugin = plugin_name

    plugin_module = get_plugin_module(plugin.package_name, plugin_name)

    plugin_class = getattr(plugin_module, plugin_name)
#    page_msg(plugin_class, type(plugin_class)
    class_instance = plugin_class(context, local_response)
    unbound_method = getattr(class_instance, method_name)

    output = unbound_method(*url_args, **method_kwargs)

    return output



def run(context, response, plugin_name, method_name, url_args=(),
                                                            method_kwargs={}):
    """
    run the plugin with and without errorhandling
    """
#    page_msg("plugin_manager.run():", plugin_name, method_name, url_args, method_kwargs
    request = context["request"]
    try:
        return _run(
            context, response, plugin_name, method_name,
            url_args, method_kwargs
        )
    except Exception, e:
        if request.debug: # don't use errorhandling -> raise the prior error
            raise

        if isinstance(e, (Http404, AccessDenied)):
            # Don't catch "normal" errors...
            raise

        msg = "Run plugin %s.%s Error" % (plugin_name, method_name)
        request.page_msg.red("%s:" % msg)
        import sys, traceback
        request.page_msg(mark_safe("<pre>%s</pre>" % traceback.format_exc()))
        return msg + "(Look in the page_msg)"


def handle_command(context, response, plugin_name, method_name, url_args):
    """
    handle a _command url request.
    If the plugin doesn't change the page title, we set it here.
    """
    original_page_title = context["PAGE"].title

    output = run(context, response, plugin_name, method_name, url_args)

    if context["PAGE"].title == original_page_title:
        # The plugin doesn't set a page title.
        if plugin_name == method_name or method_name == "lucidTag":
            title = plugin_name
        else:
            title = "%s - %s" % (plugin_name, method_name)
        context["PAGE"].title = title.replace("_", " ")

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


def get_create_table(plugin_models):
    style = no_style()

    statements = []
    for model in plugin_models:
        statements += connection.creation.sql_create_model(model, style)[0]
        statements += connection.creation.sql_indexes_for_model(model, style)
        statements += sql.custom_sql_for_model(model, style)
        statements += connection.creation.sql_for_many_to_many(model, style)
    return statements


def create_plugin_tables(plugin, page_msg, verbosity):
    plugin_models = Plugin.objects.get_plugin_models(
        plugin.package_name,
        plugin.plugin_name,
        page_msg, verbosity
    )
    if not plugin_models:
        if verbosity>1:
            page_msg.green(_("Plugin has no models, ok."))
        return

    statements = get_create_table(plugin_models)

    cursor = connection.cursor()
    for statement in statements:
        if verbosity>1:
            page_msg(statement)
        cursor.execute(statement)

    if verbosity:
        page_msg.green(_("%i plugin models installed.") % len(statements))


def _install_plugin(package_name, plugin_name, plugin_config, user, page_msg,
                                                            verbosity, active):
    """
    insert a plugin/plugin in the 'plugin' table
    """
    plugin = Plugin.objects.create(
        package_name = package_name,
        plugin_name = plugin_name,
        author = plugin_config.__author__,
        url = plugin_config.__url__,
        description = plugin_config.__description__,
        multiple_pref = getattr(plugin_config, "multiple_pref", True),
        can_deinstall = getattr(plugin_config, "__can_deinstall__", True),
        active = active,
    )

    pref_form = getattr(plugin_config, "PreferencesForm", None)
    if pref_form:
        if verbosity>1:
            page_msg("Found a preferences newform class.")
        plugin.init_pref_form(pref_form, page_msg, verbosity, user)

    plugin.save()
    if verbosity>1:
        page_msg("OK, ID:", plugin.id)

    create_plugin_tables(plugin, page_msg, verbosity)

    return plugin




@transaction.commit_on_success
def install_plugin(package_name, plugin_name, page_msg, verbosity, user,
                                                                active=False):
    """
    Get the config object from disk and insert the plugin into the database
    """
    plugin_config = get_plugin_config(package_name, plugin_name)
    if verbosity>1:
        obsolete_test = (
            hasattr(plugin_config, "__important_buildin__") or
            hasattr(plugin_config, "__essential_buildin__")
        )
        if obsolete_test:
            page_msg("*** DeprecationWarning: ***")
            page_msg(
                " - '__important_buildin__'"
                " or '__essential_buildin__'"
                " are obsolete."
            )

    plugin = _install_plugin(
        package_name, plugin_name, plugin_config,
        user, page_msg, verbosity, active
    )
    return plugin


def auto_install_plugins(debug, page_msg, verbosity=True):
    """
    Install all internal plugin how are markt as important or essential.
    """
    Plugin.objects.all().delete()    # delete all installed Plugins

    for path_cfg in settings.PLUGIN_PATH:
        if path_cfg["auto_install"] == True:
            _auto_install_plugins(debug, path_cfg, page_msg, verbosity)


def _auto_install_plugins(debug, path_cfg, page_msg, verbosity):
    package_name = ".".join(path_cfg["path"])

    plugin_path = os.path.join(*path_cfg["path"])
    plugin_list = get_plugin_list(plugin_path)

    for plugin_name in plugin_list:
        if verbosity:
            msg= "\n\ninstall '%s' plugin: *** %s ***\n" % (
                path_cfg["type"], plugin_name
            )
            page_msg.black(msg)

        try:
            plugin = install_plugin(
                package_name, plugin_name,
                page_msg, verbosity, user=None, active=True
            )
        except Exception, err:
            # FIXME
            page_msg.red("Error: %s" % err)
            import traceback
            info = "<pre>%s</pre>" % traceback.format_exc()
            info = mark_safe(info)
            page_msg.red(info)
            continue

        if verbosity:
            page_msg.green("OK, plugin ID %s installed." % plugin.id)







