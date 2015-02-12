#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid - manage.py
    ~~~~~~~~~~~~~~~~~~~


    *** Please change ROOT_DIR path to your needs!


    Check requirements

    Check some external libs with pkg_resources.require()
    We only create warnings on VersionConflict and DistributionNotFound exceptions.
    
    We use the requirements files from ./pylucid/requirements/*.txt
    
    FIXME: Can it be that pkg_resources.require("pylucid") is sufficient?
       

    origin code was borrowed from the pinax project.
    
    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
import sys
import warnings


##############################################################################
# Change this path:
ROOT_DIR = "/please/insert/path/to/PyLucid_env/"
##############################################################################

LOCAL_DEBUG = False
# LOCAL_DEBUG = True

RUN_WITH_DEV_SERVER = "runserver" in sys.argv

os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

PYLUCID_BASE_PATH = os.path.join(ROOT_DIR, "src/pylucid/pylucid_project")
sys.path.insert(0, PYLUCID_BASE_PATH)

sys.stderr = sys.stdout

print "virtualenv activate...",
virtualenv_file = os.path.join(ROOT_DIR, "bin/activate_this.py")
try:
    execfile(virtualenv_file, dict(__file__=virtualenv_file))
except Exception, err:
    print "Error: Can't activate the virtualenv!"
    print
    print "Failed to execute file %r" % virtualenv_file
    print
    print "-" * 79
    import traceback
    traceback.print_exc()
    print "-" * 79
    print
    print "ROOT_DIR = %r" % ROOT_DIR
    print "Please check ROOT_DIR in this file (%s)" % __file__
    print
    sys.exit(1)

print "OK"


#------------------------------------------------------------------------------

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
        if requirement.endswith("==dev"):
            if LOCAL_DEBUG and RUN_WITH_DEV_SERVER:
                print "Skip %r because pkg_resources.require() can't handle this, ok." % (
                    requirement
                )
            continue
        try:
            pkg_resources.require(requirement)
        except pkg_resources.VersionConflict, err:
            warnings.warn("Version conflict: %s" % err)
        except pkg_resources.DistributionNotFound, err:
            warnings.warn("Distribution not found: %s" % err)
        else:
            if LOCAL_DEBUG:
                print "Debug: %r, ok." % requirement


def get_requirements():
    def parse_requirements(filename):
        filepath = os.path.normpath(os.path.join(PYLUCID_BASE_PATH, "../requirements", filename))
        if LOCAL_DEBUG:
            print "Use %r" % filepath
        f = file(filepath, "r")
        entries = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            if line.startswith("-e "):
                line = line.split("#egg=")[1]
            if LOCAL_DEBUG:
                print line
            entries.append(line)
        f.close()
        return entries

    requirements = []
    requirements += parse_requirements("basic_requirements.txt")
    requirements += parse_requirements("normal_installation.txt")
    return requirements


#------------------------------------------------------------------------------


def _error(msg):
    print "Import Error:", msg
    print "-" * 79
    import traceback
    traceback.print_exc()
    print "-" * 79
    print "Did you activate the virtualenv?"
    sys.exit(1)

try:
    from django.core.management import execute_from_command_line
except ImportError, msg:
    _error(msg)



if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pylucid_project.settings")

    try:
        requirements = get_requirements()
        check_require(requirements)
    except Exception, e:
        if (LOCAL_DEBUG or settings_mod.DEBUG) and settings_mod.RUN_WITH_DEV_SERVER:
            raise

        sys.stderr.write("Error while check requirements:")
        sys.stderr.write(traceback.format_exc())


    try:
        execute_from_command_line(sys.argv)
    except Exception, err:
        _error("Error execute command: %s" % err)
    # except:
    #     import pdb, traceback
    #     print("-"*60)
    #     traceback.print_exc()
    #     print("-"*60)
    #     pdb.post_mortem()
