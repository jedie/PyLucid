#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid internal page
    ~~~~~~~~~~~~~~~~~~~~~

    API to the internal page templates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, posixpath

from django.conf import settings


INTERNAL_PAGE_EXT = ("html", "css", "js")

class InternalPage(object):
    """
    Some path information for building URLs and filesystem path to the default
    and customized internal pages.

    "internal_page_url" - for building URL to the default internal page
    "internal_page_root" - filesystem path to default internal pages

    "custom_internal_page_url" - for customized internal pages URLs
    "custom_internal_page_root" - filesystem path to customized internal pages
    """
    def __init__(self, context, plugin_name):
        self.request     = context["request"]
        self.page_msg    = self.request.page_msg
        self.URLs        = context["URLs"]

        self.plugin_name = plugin_name

        # Set url/path for the current plugin:

        self.default_plugin_root = os.path.join(
            self.URLs["internal_page_root"], plugin_name
        )
        self.default_plugin_url = posixpath.join(
            self.URLs["internal_page_url"], plugin_name
        )
        self.custom_plugin_root = os.path.join(
            self.URLs["custom_internal_page_root"], plugin_name
        )
        self.custom_plugin_url = posixpath.join(
            self.URLs["custom_internal_page_url"], plugin_name
        )

    def get_filename(self, internal_page_name, slug):
        """
        returns the filename of the specific internal page.
        """
        return internal_page_name + "." + slug

    def get_file_path_and_url(self, internal_page_name, slug):
        """
        returns the path and the url to the given filename.
        """
        filename = self.get_filename(internal_page_name, slug)

        data = [
            (self.custom_plugin_root, self.custom_plugin_url),
            (self.default_plugin_root, self.default_plugin_url),
        ]
        for path, url in data:
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                file_url = posixpath.join(url, filename)
                return (file_path, file_url)

        return (None, None)

    def get_content(self, internal_page_name, slug):
        """
        returns the content of a internal page.
        slug = "html", "css" or "js"
        """
        file_path, file_url = self.get_file_path_and_url(
            internal_page_name, slug
        )
        if file_path == None:
            # File not found
            if slug in ("css", "js"):
                # CSS and JS files are optional
                return u""
            else:
                msg = "Internal page '%s' not found in %s or %s" % (
                    internal_page_name, self.custom_plugin_root,
                    self.default_plugin_root
                )
                raise InternalPageNotFound(msg)

        f = file(file_path, "r")
        content = f.read()
        f.close()
        content = content.decode(settings.FILE_CHARSET)
        return content

    def get_url(self, internal_page_name, slug):
        """
        Return the url to the linked internal page parts.
        Returns None if the file not exists. (CSS and JS are optional).
        """
        file_path, file_url = self.get_file_path_and_url(
            internal_page_name, slug
        )
        return file_url


def get_internal_page(context, plugin_name, internal_page_name):
    """
    shortcut function for request the html content of the internal page.
    Used in page_style plugin.
    """
    internal_page = InternalPage(context, plugin_name)
    content = internal_page.get_content(internal_page_name, "html")
    return content


class InternalPageNotFound(Exception):
    pass


