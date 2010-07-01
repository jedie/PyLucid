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

    src_base_path = os.path.join(env_path, "src")

    src_package_info = {}

    for src in os.listdir(src_base_path):
        src_path = os.path.join(src_base_path, src)

        if os.path.isdir(os.path.join(src_path, ".svn")):
            info_cmd = ["svn", "info"]
        elif os.path.isdir(os.path.join(src_path, ".git")):
#            info_cmd = ["git", "status"]
            info_cmd = ["git", "log", "-1", "HEAD"]
        else:
            src_package_info[src] = "Error: no .svn or .git dir found!"
            continue

        process = subprocess.Popen(
            info_cmd,
            cwd=src_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = process.stdout.read()
        output += process.stderr.read()
        src_package_info[src] = output

    context.update({
        "env_path": env_path,
        "src_package_info": src_package_info,
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

    src_path = os.path.join(env_path, "src", src_name)
    if not os.path.isdir(src_path):
        messages.error(request, "Wrong path: %r" % src_path)
        return context

    if os.path.isdir(os.path.join(src_path, ".svn")):
        cmd = ["svn", "update"]
    elif os.path.isdir(os.path.join(src_path, ".git")):
        cmd = ["git", "pull", "origin", "master"]
    else:
        messages.error(request, "Wrong path: %r" % src_path)
        return context

    process = subprocess.Popen(
        cmd,
        cwd=src_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = process.stdout.read()
    output += process.stderr.read()

    context.update({
        "env_path": env_path,
        "package_name": src_name,
        "output": output,
    })
    return context
