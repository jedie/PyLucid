# coding: utf-8

"""
    Check some external libs with pkg_resources.require()
    We only create warnings on VersionConflict and DistributionNotFound exceptions.
    
    See also: ./scripts/requirements/external_apps.txt
    See also: ./scripts/requirements/libs.txt
    
    Format info for pkg_resources.require():
    http://peak.telecommunity.com/DevCenter/PkgResources#requirement-objects
"""

import warnings

import pkg_resources

def check_require(requirements):
    """
    Check a package list.
    Display only warnings on VersionConflict and DistributionNotFound exceptions.
    """
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
        except pkg_resources.VersionConflict, err:
            warnings.warn("Version conflict: %s" % err)
        except pkg_resources.DistributionNotFound, err:
            warnings.warn("Distribution not found: %s" % err)


requirements = (
    # http://code.google.com/p/django-dbpreferences
    "django-dbpreferences >= 0.3.1beta",

    # http://code.google.com/p/django-tools/
    "django-tools >= 0.8",

    # http://code.google.com/p/python-creole/
    "python-creole >= 0.2.4",

    # http://code.google.com/p/django-reversion/
    "django-reversion >= 1.1.2",

    # http://code.google.com/p/django-dbtemplates/
    "django-dbtemplates >= 0.5.8",

    # http://code.google.com/p/django-tagging/
    "django_tagging > 0.3",
)

check_require(requirements)
