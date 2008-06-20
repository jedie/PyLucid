# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

#_____________________________________________________________________________
# meta information
__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "edit a CMS page"
__long_description__    = """
-Edit/delete existing pages.
-Create new pages.
-Setup the page order in the menu.
"""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "new_page" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "delete_page" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "markup_help" : {
        "must_login" : False,
        "must_admin" : False,
    },
    "select_edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "admin_sub_menu": {
            "section"       : _("page admin"),
            "title"         : _("select page to edit"),
            "help_text"     : _("all pages available!"),
            "open_in_window": False,
            "weight"        : -8,
        },
    },
    "delete_pages" : {
        "must_login" : True,
        "must_admin" : True,
        "admin_sub_menu": {
            "section"       : _("page admin"),
            "title"         : _("delete pages"),
            "help_text"     : _("select pages to delete these."),
            "open_in_window": False,
            "weight"        : -5,
        },
    },
    "sequencing" : {
        "must_login"    : True,
        "must_admin"    : False,
        "admin_sub_menu": {
            "section"       : _("page admin"),
            "title"         : _("sequencing the pages"),
            "help_text"     : _("change the page order."),
            "open_in_window": False,
            "weight"        : -3,
        },
    },
    "tag_list": {
        "must_login" : False,
        "must_admin" : False,
    },
    "page_link_list": {
        "must_login" : True,
        "must_admin" : False,
    },
}
