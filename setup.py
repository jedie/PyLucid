#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid-boot
    ~~~~~~~~~~~~
    
    Scripts for creating a `PyLucid`_ virtual environment.

    .. _PyLucid:
        http://www.pylucid.org

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from setuptools import setup, find_packages

from pylucid_boot import VERSION_STRING

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_authors():
    authors = []
    try:
        f = file(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r")
        for line in f:
            if line.startswith('*'):
                authors.append(line[1:].strip())
        f.close()
    except Exception, err:
        authors = ["Error: can't get AUTHORS: %s" % err]
    return authors


setup(
    name = 'PyLucid-boot',
    version = VERSION_STRING,
    description = 'PyLucid-boot are some scripts for creating a PyLucid virtual environment',
    long_description = __doc__,
    author = get_authors(),
    maintainer = "Jens Diemer",
    maintainer_email = "PyLucid-boot@jensdiemer.de",
    url = 'http://github.com/jedie/PyLucid-boot',
    packages = find_packages(),
    platforms = 'any',
    include_package_data = True, # include package data under svn source control
    zip_safe = True,
    classifiers = [
        "Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
#        "Development Status :: 3 - Alpha",
#        "Development Status :: 4 - Beta",
#        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
#        "Intended Audience :: Education",
#        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        'Framework :: Django',
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ]
)
