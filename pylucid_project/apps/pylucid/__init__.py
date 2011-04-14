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

try:
    import pkg_resources
except ImportError, e:
    import sys
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
        try:
            pkg_resources.require(requirement)
        except pkg_resources.VersionConflict, err:
            warnings.warn("Version conflict: %s" % err)
        except pkg_resources.DistributionNotFound, err:
            warnings.warn("Distribution not found: %s" % err)


requirements = (
    # http://www.djangoproject.com/
    "django > 1.2",

    # http://code.google.com/p/django-dbpreferences
    "django-dbpreferences >= 0.4.0",

    # http://code.google.com/p/django-tools/
    "django-tools >= 0.15.0",

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
