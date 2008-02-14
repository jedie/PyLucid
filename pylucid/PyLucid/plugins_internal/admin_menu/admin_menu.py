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


from PyLucid.system.BasePlugin import PyLucidBasePlugin


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
        render the sub menu
        """
        is_admin = self.request.user.is_superuser or self.request.user.is_staff

        context = {
            "PAGE"            : self.context["PAGE"],
            "commandURLprefix": self.URLs.get_command_base(),
            "adminURLprefix"  : self.URLs["adminBase"],
            "is_admin"        : is_admin,
        }
        self._render_template("sub_menu", context)#, debug=True)



