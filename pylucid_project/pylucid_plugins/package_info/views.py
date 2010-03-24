# coding: utf-8

"""
    PyLucid packages information plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__ = "$Rev:$"

import os

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"
    virtualenv_file = "../../../../../bin/activate_this.py"
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

import pkg_resources

import django
from django.conf import settings
from django.template import mark_safe
from django.utils.version import get_svn_revision

from pylucid_project import VERSION_STRING
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
    'feedparser',
    'pip',
    'pygments',
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
    "license_url": "http://bitbucket.org/jezdez/django-dbtemplates/src/tip/LICENSE",
}
STATIC_PKG_INFO["django-reversion"] = {
    "license": "New BSD",
    "license_url": "http://code.google.com/p/django-reversion/source/browse/trunk/LICENSE",
}
STATIC_PKG_INFO["pylucid"] = {
    "license": "GNU GPL v3 or above",
    "license_url": "http://www.pylucid.org/permalink/37/License/",
    "version": VERSION_STRING,
}
STATIC_PKG_INFO["pip"] = {
    "license_url": "http://bitbucket.org/ianb/pip/src/tip/docs/license.txt",
}
STATIC_PKG_INFO["pygments"] = {
    "license_url": "http://dev.pocoo.org/projects/pygments/browser/LICENSE",
}
STATIC_PKG_INFO["python-creole"] = {
    "license": "GNU GPL v3 or above",
    "license_url": "http://code.google.com/p/python-creole/source/browse/trunk/LICENSE",
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
        self._add_svn_reversion()

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

    def _add_svn_reversion(self):
        """ Add Subverion reversion number to version string, if exist """
        location = dict.get(self, "location")
        svn_revision = get_svn_revision(location)
        if svn_revision == "SVN-unknown":
            return

        if svn_revision not in self["version"]:
            self["version"] += " %s" % svn_revision


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
        request.page_msg("Debug existing package template keys:")
        existing_keys = package_info.existing_keys()
        for key in sorted(existing_keys):
            request.page_msg(mark_safe(
                "<i>entry</i><strong>.%s</strong>" % key
            ))


    return context


if __name__ == "__main__":
    from pprint import pprint

    print package_info.existing_keys()
    pprint(package_info)

