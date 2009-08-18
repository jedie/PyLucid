# coding: utf-8

"""
    Check some external libs with pkg_resources.require()
    
    See also: ./scripts/requirements/external_apps.txt
    See also: ./scripts/requirements/libs.txt
    
    Format info for pkg_resources.require():
    http://peak.telecommunity.com/DevCenter/PkgResources#requirement-objects
"""


import pkg_resources

# http://code.google.com/p/django-dbpreferences
pkg_resources.require('django-dbpreferences >= 0.3.1beta')

# http://code.google.com/p/django-tools/
pkg_resources.require('django-tools >= 0.4.0beta')

# http://code.google.com/p/python-creole/
pkg_resources.require('python-creole >= 0.2.4')


# http://code.google.com/p/django-reversion/
pkg_resources.require('django-reversion >= 1.2')

# http://code.google.com/p/django-dbtemplates/
pkg_resources.require('django-dbtemplates >= 0.5.8')

# http://code.google.com/p/django-tagging/
pkg_resources.require('tagging >= 0.3-pre')
