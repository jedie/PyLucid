# coding: utf-8

"""
    Check requirements
    ~~~~~~~~~~~~~~~~~~

    Check some external libs with pkg_resources.require()
    We only create warnings on VersionConflict and DistributionNotFound exceptions.
    
    We use the requirements files from ./pylucid/requirements/*.txt
    
    FIXME: Can it be that pkg_resources.require("pylucid") is sufficient?
       
    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import warnings
import traceback

from django.conf import settings

#DEBUG = True
DEBUG = False

try:
    import pkg_resources
except ImportError, e:
    etype, evalue, etb = sys.exc_info()
    evalue = etype(
        (
            "%s - Have you installed setuptools?"
            " See: http://pypi.python.org/pypi/setuptools"
            " - Or is the virtualenv not activated?"
        ) % evalue
    )
    raise etype, evalue, etb


def check_require(requirements):
    """
    Check a package list.
    Display only warnings on VersionConflict and DistributionNotFound exceptions.
    """
    for requirement in requirements:
        if requirement == "pylucid":
            # Skip, because pkg_resources.require() would check all requirement from pylucid, too.
            continue
        if DEBUG and settings.RUN_WITH_DEV_SERVER:
            print requirement
        try:
            pkg_resources.require(requirement)
        except pkg_resources.VersionConflict, err:
            warnings.warn("Version conflict: %s" % err)
        except pkg_resources.DistributionNotFound, err:
            warnings.warn("Distribution not found: %s" % err)


def get_requirements():
    def parse_requirements(filename):
        filepath = os.path.normpath(os.path.join(settings.PYLUCID_BASE_PATH, "../requirements", filename))
        if DEBUG and settings.RUN_WITH_DEV_SERVER:
            print "Use %r" % filepath
        f = file(filepath, "r")
        entries = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            if line.startswith("-e "):
                line = line.split("#egg=")[1]
            if DEBUG and settings.RUN_WITH_DEV_SERVER:
                print line
            entries.append(line)
        f.close()
        return entries

    requirements = []
    requirements += parse_requirements("basic_requirements.txt")
    requirements += parse_requirements("normal_installation.txt")
    return requirements

try:
    requirements = get_requirements()
    check_require(requirements)
except Exception, e:
    if (DEBUG or settings.DEBUG) and settings.RUN_WITH_DEV_SERVER:
        raise

    sys.stderr.write("Can't check requirements:")
    sys.stderr.write(traceback.format_exc())
