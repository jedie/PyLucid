# coding: utf-8

"""
    filemanager
    ~~~~~~~~~~~

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import posixpath

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext as _


DEFAULT_UNAUTHORIZED_SIGNS = ("..", "//", "\\")


class FilemanagerError(Exception):
    """
    for errors with a message to staff/admin users.
    e.g.: Gallery filesystem path doesn't exist anymore.
    """
    pass


class DirectoryTraversalAttack(FilemanagerError):
    """
    Some unauthorized signs are found or the path is out of the base path.
    """
    pass


class BaseFilemanager(object):
    """
    Base class for a django app like a filemanager.
    """
    def __init__(self, request, absolute_path, base_url, rest_url, unauthorized_signs=None):
        """
        absolute_path - path in filesystem to the root directory
        base_url - url prefix of this filemanager instance
        rest_url - relative sub path of the current view

        it is assumed that 'absolute_path' and 'base_url' are internal values
        and 'rest_url' are a external given value from the requested user.
        """
        self.request = request

        # characters that aren't allowed in the path.
        # To protect from: https://en.wikipedia.org/wiki/Directory_traversal_attack
        if unauthorized_signs is None:
            self.unauthorized_signs = DEFAULT_UNAUTHORIZED_SIGNS
        else:
            self.unauthorized_signs = unauthorized_signs
        assert isinstance(self.unauthorized_signs, (list, tuple)), "'unauthorized_signs' must be a list or tuples!"

        self.absolute_path = absolute_path
        self.base_url = base_url

        self.check_unauthorized_sign(rest_url)
        if rest_url.startswith("/"):
            rest_url = rest_url[1:]
        self.rel_path = os.path.normpath(rest_url)
        self.rel_url = posixpath.normpath(self.rel_path)

        self.abs_path = os.path.normpath(os.path.join(self.absolute_path, self.rel_path))
        self.check_unauthorized_sign(self.abs_path) # not really necessary
        self.check_path(absolute_path, self.abs_path)

        self.abs_url = posixpath.normpath(posixpath.join(self.base_url, self.rel_url))

        if not os.path.isdir(self.abs_path):
            raise FilemanagerError("Builded path %r doesn't exist." % self.abs_path)

        self.breadcrumbs = self.build_breadcrumbs()

    def build_breadcrumbs(self):
        parts = ""
        url = self.base_url
        breadcrumbs = [{
            "name": _("index"),
            "title": _("goto 'index'"),
            "url": url
        }]
        rel_url = self.rel_url.strip("/")
        if not rel_url:
            return breadcrumbs

        for url_part in rel_url.split("/"):
            url += "%s/" % url_part
            parts += "%s/" % url_part
            breadcrumbs.append({
                "name": url_part,
                "title": _("goto '%s'") % parts,
                "url": url
            })
        return breadcrumbs

    def check_unauthorized_sign(self, value):
        for sign in self.unauthorized_signs:
            if sign and sign in value:
                raise DirectoryTraversalAttack("%r found in %s" % (sign, repr(value)))

    def check_path(self, base_path, path):
        """
        Simple check if the path is a sub directory of base_path.
        This must be called from external!
        """
        if not path.startswith(base_path):
            raise DirectoryTraversalAttack("%r doesn't start with %r" % (path, base_path))


