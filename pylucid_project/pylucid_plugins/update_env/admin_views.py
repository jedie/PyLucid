# coding: utf-8

"""
    PyLucid admin views
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import subprocess

from django import http
from django.conf import settings
from django.contrib import messages
from django.core import management
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu




def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")
    admin_menu.add_menu_entry(
        parent=menu_section_entry, url_name="Update-status",
        name="update virtualenv", title="Update virtual environment source packages",
    )

    return "\n".join(output)


def _get_env_path(request):
    env_path = request.META.get("VIRTUAL_ENV")
    if env_path is None:
        base_path = settings.PYLUCID_BASE_PATH
        messages.info(request,
            "Environment Variable 'VIRTUAL_ENV' not set."
            " Try to use %r" % base_path
        )
        try: # FIXME: do this better ;)
            env_path, rest = base_path.split(os.sep + "src" + os.sep)
        except ValueError:
            messages.error(request, "Can't split %r" % base_path)
            return

    if not os.path.isdir(env_path):
        messages.error(request,
            "Error: Env.path %r doesn't exist."
            " (used from Environment Variable 'VIRTUAL_ENV')" % env_path
        )
        return

    return env_path


class Package(object):
    SVN = 1
    GIT = 2
    STATUS_CMD = {
        SVN: ["svn", "info"],
        GIT: ["git", "log", "-1", "HEAD"],
    }
    UPDATE_CMD = {
        SVN: ["svn", "update"],
        GIT: ["git", "pull", "origin"]
    }

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.output = u"Not collected yet."

        if os.path.isdir(os.path.join(path, ".svn")):
            self.type = self.SVN
        elif os.path.isdir(os.path.join(path, ".git")):
            self.type = self.GIT
        else:
            self.type = None

    def _cmd(self, cmd_dict):
        """ subprocess the VCS command and store ouput in self.output """
        assert self.type is not None
        cmd = cmd_dict[self.type]

        process = subprocess.Popen(
            cmd, cwd=self.path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.output = process.stdout.read()
        self.output += process.stderr.read()

    def collect_status(self):
        """ call STATUS_CMD and save the output in self.output """
        self._cmd(self.STATUS_CMD)

    def update(self):
        """ call UPDATE_CMD and save the output in self.output """
        self._cmd(self.UPDATE_CMD)


class VCS_info(object):
    def __init__(self, env_path):
        self.env_path = env_path

        self.package_info = {}

        self.read_src()
        self.read_external_plugins()

    def _add_path(self, abs_path):
        package = Package(abs_path)
        if package.type is not None:
            self.package_info[package.name] = package

    def read_src(self):
        """
        init packages from PyLucid_env/src/
        """
        base_path = os.path.join(self.env_path, "src")
        for dir in os.listdir(base_path):
            abs_path = os.path.join(base_path, dir)
            self._add_path(abs_path)

    def read_external_plugins(self):
        """
        init packages from PyLucid_env/src/pylucid/pylucid_project/external_plugins/
        """
        base_path = os.path.join(self.env_path, "src", "pylucid", "pylucid_project", "external_plugins")
        for dir in os.listdir(base_path):
            abs_path = os.path.join(base_path, dir)
            if not os.path.islink(abs_path):
                self._add_path(abs_path)
            else:
                # dissolving symlinks
                real_path = os.path.realpath(abs_path)
                plugin_base_path = os.path.split(real_path)[0] # PyLucid plugins used a subdirectory
                self._add_path(plugin_base_path)

    def collect_all_status(self):
        """
        Collect 'SVN info' or 'git log' for all packages.
        """
        for package in self.package_info.values():
            package.collect_status()




@check_permissions(superuser_only=True)
@render_to("update_env/status.html")
def status(request):
    """
    Update virtual environment source packages
    """
    context = {
        "title": _("virtual environment source package status"),
        "form_url": request.path,
    }
    env_path = _get_env_path(request)
    if env_path is None:
        return context # virtualenv path unknown, page_mags was created

    vcs_info = VCS_info(env_path)
    vcs_info.collect_all_status()

    context.update({
        "env_path": env_path,
        "vcs_info": vcs_info,
    })
    return context


@check_permissions(superuser_only=True)
@render_to("update_env/update.html")
def update(request, src_name):
    context = {
        "title": _("Update source package '%s'" % src_name),
        "form_url": request.path,
    }
    env_path = _get_env_path(request)
    if env_path is None:
        return context # virtualenv path unknown, page_mags was created

    vcs_info = VCS_info(env_path)
    if src_name not in vcs_info.package_info:
        messages.error(request, "Wrong package!")
        return context

    package = vcs_info.package_info[src_name]
    package.update()

    context.update({
        "env_path": env_path,
        "package": package
    })
    return context
