# coding: utf-8

"""
    PyLucid packages information plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2010-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

import os
import subprocess
import sys
import traceback
import time

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    virtualenv_file = "../../../../../bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

import pkg_resources

import django
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe

from pylucid_project import VERSION_STRING, get_commit_timestamp
from pylucid_project.apps.pylucid.decorators import render_to

# print (!) some debug info. Values can be: False, 1, 2
DEBUG = False

# Collect only information about these packages:
PACKAGES = (
    'django',
    'django-dbpreferences',
    'django-dbtemplates',
    'django-reversion',
    'django-tagging',
    'django-tools',
    'django-processinfo',
    'feedparser',
    'pip',
    'pygments',
    'south',
    'pylucid',
    'python-creole'
)

# Default packages information
# Importand:
#       Information stored in STATIC_PKG_INFO would not be overwritten!
STATIC_PKG_INFO = dict.fromkeys(PACKAGES, {})

STATIC_PKG_INFO["django"] = {
    "license": "BSD",
    "license_url": "http://code.djangoproject.com/browser/django/trunk/LICENSE",
    "version": django.get_version(),
}
STATIC_PKG_INFO["django-dbtemplates"] = {
    "license": "BSD",
    "license_url": "https://github.com/jezdez/django-dbtemplates/blob/develop/LICENSE",
}
STATIC_PKG_INFO["django-reversion"] = {
    "license": "New BSD",
    "license_url": "https://github.com/etianen/django-reversion/blob/master/LICENSE",
}
STATIC_PKG_INFO["pylucid"] = {
    "license": "GNU GPL v3 or above",
    "license_url": "http://www.pylucid.org/permalink/37/License/",
    "version": VERSION_STRING,
}
STATIC_PKG_INFO["pip"] = {
    "license_url": "https://github.com/pypa/pip/blob/develop/LICENSE.txt",
}
STATIC_PKG_INFO["pygments"] = {
    "license_url": "https://bitbucket.org/birkenfeld/pygments-main/src/tip/LICENSE",
}
STATIC_PKG_INFO["python-creole"] = {
    "license": "GNU GPL v3 or above",
    "license_url": "https://github.com/jedie/python-creole/blob/master/LICENSE",
}
STATIC_PKG_INFO["django-processinfo"] = {
    "license": "GNU GPL v3 or above",
    "license_url": "https://github.com/jedie/django-processinfo/blob/master/LICENSE",
}


# Attribute names witch are transfered from
# Distribute package object into the package info dict
PKG_DIST_ATTRS = (
    "version", "project_name", "location",
)

# keys witched are used from PKG-INFO file
PKG_INFO_KEYS = (
    "Summary",
    "Home-page",
    "Author",
    "Author-email",
    "License",
    "Download-URL"
)



class PackageInfo(dict):
    " Holds all package information for *one* package "
    def __init__(self, pkg_dist, defaults):
        self.pkg_dist = pkg_dist
        dict.__init__(self, defaults)

        self._fill_with_dist_attr()
        self._fill_with_pkg_info()
        self._add_vcs_reversion()

    def _fill_with_dist_attr(self):
        """
        Add package informations from package distribution object attributes
        But only if:
            -Attribute name exist in PKG_DIST_ATTRS
            -not exist
        """
        for attr_name in PKG_DIST_ATTRS:
            dist_value = getattr(self.pkg_dist, attr_name)
            dist_value = unicode(dist_value, encoding="utf-8", errors="replace")
            existing_value = dict.get(self, attr_name, None)
            if not existing_value:
                dict.__setitem__(self, attr_name, dist_value)
            elif DEBUG:
                print "*** Do not overwrite PKG_DIST_ATTRS %r:" % attr_name
                print "static: %r" % existing_value
                print "dist. value: %r" % dist_value

    def _fill_with_pkg_info(self):
        """
        Add package informations from PKG-INFO
        but only if:
            -key is in PKG_INFO_KEYS
            -not exist

        FIXME: How can we get PKG-INFO as a dict and not via get_metadata_lines?
        """
        try:
            metadata_lines = self.pkg_dist.get_metadata_lines("PKG-INFO")
        except IOError, err:
            if DEBUG:
                print "Can't get PKG-INFO:", err
            return

        for line in metadata_lines:
            if ":" not in line:
                continue

            line = unicode(line, encoding="utf-8", errors="replace")
            key, pkg_info_value = line.split(":", 1)

            if key not in PKG_INFO_KEYS:
                if DEBUG > 1:
                    print "Skip PKG-INFO %r (not in PKG_INFO_KEYS)" % key
                continue

            dict_key = key.lower().replace("-", "_")
            if DEBUG > 1 and key != dict_key:
                print "convert %r to %r" % (key, dict_key)

            pkg_info_value = pkg_info_value.strip()

            if dict.__contains__(self, dict_key):
                if DEBUG:
                    print "*** Do not overwrite PKG-INFO %r:" % dict_key
                    print "static: %r" % dict.__getitem__(self, dict_key)
                    print "PKG-INFO: %r" % pkg_info_value
                continue

            dict.__setitem__(self, dict_key, pkg_info_value)

    def _add_vcs_reversion(self):
        """ Add subversion/git reversion number to version string, if exist """

        if "git" in self["version"]:
            return

        location = dict.get(self, "location")

        git_dir = os.path.join(location, ".git")
        if os.path.isdir(git_dir):
            commit_info = self.get_commit_info(location)
            if commit_info:
                self["version"] += " - Last git commit: %s" % commit_info

    def get_commit_info(self, path):
        # %ct: committer date, UNIX timestamp
        cmd = ["/usr/bin/git", "log", "--pretty=format:%ct", "-1", "HEAD"]
        try:
            process = subprocess.Popen(cmd, shell=False, cwd=path,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except Exception:
            if settings.DEBUG:
                # insert more information into the traceback and re-raise the original error
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    'subprocess error, running %r: %s)' % (
                        " ".join(cmd), evalue
                    )
                )
                raise etype, evalue, etb
            return

        process.wait()
        returncode = process.returncode
        output = process.stdout.read().strip()
        error = process.stderr.read().strip()
        if returncode != 0:
            if settings.DEBUG:
                raise RuntimeError(
                    "Can't get git hash, returncode was: %r"
                    " - git stdout: %r"
                    " - git stderr: %r"
                    % (returncode, output, error)
                )
            return

        try:
            timestamp = int(output)
        except Exception:
            if settings.DEBUG:
                # insert more information into the traceback and re-raise the original error
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    'git stdout: %r - git stderr: %r - (Original error: %s)' % (
                        output, error, evalue
                    )
                )
                raise etype, evalue, etb
            return

        try:
            return time.strftime("%d.%m.%Y", time.gmtime(timestamp))
        except Exception:
            if settings.DEBUG:
                # insert more information into the traceback and re-raise the original error
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    "Can't convert %s: %s" % (
                        repr(timestamp), evalue
                    )
                )
                raise etype, evalue, etb
            return


class EnvironmetInfo(dict):
    " dict with all packages information "
    def __init__(self, static_pkg_info):
        pkg_env = pkg_resources.Environment()

        # fill all informations for all packages
        for pkg_key in pkg_env:
            pkg_dist = pkg_env[pkg_key][0]

            defaults = static_pkg_info.get(pkg_key, None)
            if defaults is None:
                defaults = {"is_relevant": False}
            else:
                defaults["is_relevant"] = True

            dict.__setitem__(self, pkg_key, PackageInfo(pkg_dist, defaults))

    def existing_keys(self):
        """ returns a list of all existing package info keys """
        existing_keys = set()
        for pkg_info_dict in package_info.values():
            keys = pkg_info_dict.keys()
            existing_keys = existing_keys.union(set(keys))
        return list(existing_keys)


package_info = EnvironmetInfo(STATIC_PKG_INFO)


@render_to("package_info/packages_table.html")
def lucidTag(request, all_packages=False, display_version=False, display_location=False, debug=False):
    """
    List all used Python modules with there version number.

    all_packages: True, False (default)
        Display all existing packages in the current environment?
        Normally, only the relevant packets are displayed.

    display_version: True, False (default)
        Add the version string to every packages?

    display_location: True, False (default)
        Display the absolute filesystem location of the package.

    debug: True, False (default)
        -List all existing package template keys: Needfull if you overwrite the template.

    Note: Display version and location is not good for security.

    example:
        {% lucidTag package_info %}
        {% lucidTag package_info all_packages=True %}
        {% lucidTag package_info display_version=True %}
        {% lucidTag package_info display_location=True %}
        {% lucidTag package_info debug=True %}
    """
    package_info_list = package_info.values()
    package_info_list.sort(
        cmp=lambda x, y: cmp(x["project_name"].lower(), y["project_name"].lower())
    )

    context = {
        "package_info_list": package_info_list,
        "all_packages": all_packages,
        "display_version": display_version,
        "display_location": display_location,
    }

    if debug and (settings.DEBUG or request.user.is_staff):
        messages.info(request, "Debug existing package template keys:")
        existing_keys = package_info.existing_keys()
        for key in sorted(existing_keys):
            messages.info(request, mark_safe(
                "<i>entry</i><strong>.%s</strong>" % key
            ))


    return context


if __name__ == "__main__":
    from pprint import pprint

    print package_info.existing_keys()
    pprint(package_info)

