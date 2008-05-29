#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid admin menu
    ~~~~~~~~~~~~~~~~~~

    The administration top and sub menu.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Plugin
from PyLucid.system.plugin_manager import get_plugin_list, install_plugin
from PyLucid.system.plugin_import import get_plugin_config, get_plugin_version


class MenuSection(object):
    """
    Container for all entries in a admin sub menu section
    """
    def __init__(self, page_msg, section_name, section_weight):
        self.page_msg = page_msg
        self.name = section_name
        self.weight = section_weight
        self.data = []

    def add_method(self, menu_data):
        self.data.append(menu_data)

    def __iter__(self):
        """
        for django template engine
        """
        data = sorted(self.data, key=lambda x: x.get('weight',0))
        for entry in data:
            yield entry

    def __repr__(self):
        return repr(self.data)


class Menu(object):
    """
    Container for the complete admin sub menu data
    """
    def __init__(self, page_msg, section_weights):
        self.page_msg = page_msg
        self.section_weights = section_weights
        self.data = {}

    def add_entry(self, section_name, menu_data):
        if section_name not in self.data:
            # Create new section
            weights = self.section_weights
            section_weight = weights.get(section_name, 0)
            self.data[section_name] = MenuSection(
                self.page_msg, section_name, section_weight
            )

        section = self.data[section_name]
        section.add_method(menu_data)

    def __iter__(self):
        """
        for django template engine
        """
        sections = self.data.keys()
        weights = self.section_weights

        # sort in two steps:
        sections = [(weights.get(s, 0), s) for s in sections]
        sections = [x[1] for x in sorted(sections)]

        # FIXME: sorting in one step, but it doesn't work, why?
#        sections = sorted(sections, key=lambda x: weights.get(x, 0))

        for section in sections:
            yield self.data[section]

    def debug(self):
        """
        Display all data
        """
        self.page_msg("Menu debug:")
        self.page_msg(self.section_weights)
        self.page_msg(self.data)



class admin_menu(PyLucidBasePlugin):

    def lucidTag(self):
        """
        Render the front menu
        """
        current_page_id  = self.current_page.id
        edit_link = self.URLs.adminLink("PyLucid/page/%s/" % current_page_id)

        context = {
            "login_link"    : self.context["login_link"],
            "edit_page_link": self.URLs.commandLink("page_admin", "edit_page"),
            "new_page_link" : self.URLs.commandLink("page_admin", "new_page"),
            "sub_menu_link" : self.URLs.methodLink("sub_menu"),
        }
        self._render_template("top_menu", context)#, debug=True)

    def sub_menu(self):
        """
        render the admin sub menu
        """
        # Collect all plugin methods with a admin_sub_menu data dict
        menu = self._generate_menu()
        #menu.debug()

        # Get some static links to the django admin panel
        self._add_static_entries(menu)
        #menu.debug()

        #----------------------------------------------------------------------
        # Change the global page title:
        self.context["PAGE"].title = _("Administration sub menu")

        is_admin = self.request.user.is_superuser or self.request.user.is_staff

        context = {
            "dynamic_menu" : menu,
        }
        self._render_template("sub_menu", context)#, debug=True)

    def _add_static_entries(self, menu):
        """
        Adds some static sub menu entries to the django admin panel
        TODO: Make this dynamic changeable
        """
        if not self.request.user.is_staff:
            # All entries here are in the django admin panel
            # Skip all links, if the current user can't use it
            return

        page_obj = self.context["PAGE"]

        def add_entry(section, link, title, help_text="", weight=0):
            menu.add_entry(
                section,
                menu_data = {
                    #"section"       : section,
                    "link"          : link,
                    "title"         : title,
                    "help_text"     : help_text,
                    "open_in_window": True,
                    "weight" : weight,
                },
            )

        section = _("edit look")

        # STYLE
        add_entry(section,
            self.URLs.adminLink("PyLucid/style/%s" % page_obj.style.id),
            _("edit '%s' stylesheet") % page_obj.style,
            _("The current used stylesheet."),
            -5,
        )
        add_entry(section,
            self.URLs.adminLink("PyLucid/style"),
            _("edit all stylesheets"),
            "You get a list of all existing stylesheets.",
            -4,
        )

        # TEMPLATE
        add_entry(section,
            self.URLs.adminLink("PyLucid/template"),
            _("edit all templates"),
            "You get a list of all existing templates.",
            8,
        )
        add_entry(section,
            self.URLs.adminLink("PyLucid/template/%s" % page_obj.template.id),
            _("edit '%s' template") % page_obj.template,
            _("The current used template."),
            5,
        )

        section = _("user management")

        add_entry(section,
            self.URLs.adminLink("auth/user"),
            _("edit users"),
            "Edit all existing users.",
            5,
        )
        add_entry(section,
            self.URLs.adminLink("auth/group"),
            _("edit user groups"),
            "Edit all existing users.",
            5,
        )


    def _generate_menu(self):
        """
        Generate the dynamic admin sub menu
        """
        # Get the preferences from the database:
        preferences = self.get_preferences()
        if preferences == None:
            # preferences not in database -> reinit required
            if self.request.debug == True:
                msg = (
                    '<a href="http://www.pylucid.org/_goto/121/changes/">'
                    'reinit "admin_menu" plugin required!</a>'
                )
                self.page_msg.red(mark_safe(msg))
            section_weights = {}
        else:
            # Sort the sections with the weight information from the preferences
            section_weights = preferences["section_weights"]

        # All installed + active plugins
        plugins = Plugin.objects.all().filter(active = True).order_by(
            'package_name', 'plugin_name'
        )

        menu = Menu(self.page_msg, section_weights)

        # Get the plugin config and build the menu data
        for plugin in plugins:
            config = get_plugin_config(
                package_name = plugin.package_name,
                plugin_name = plugin.plugin_name,
                debug = False,
            )

            for method, data in config.plugin_manager_data.iteritems():
                if "admin_sub_menu" not in data:
                    # This method should not listed into the admin sub menu
                    continue

                menu_data = data["admin_sub_menu"]
                section = unicode(menu_data["section"]) # translate gettext_lazy

                # Add the _command link to the menu data
                link = self.URLs.commandLink(
                    plugin_name = plugin.plugin_name,
                    method_name = method,
                )
                menu_data["link"] = link

                menu.add_entry(section, menu_data)

        return menu