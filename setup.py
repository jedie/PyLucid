#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid distutils setup
    ~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.getcwd(), "pylucid_project"))
from pylucid_project import PYLUCID_VERSION_STRING


def get_authors():
    authors = []
    f = file("AUTHORS", "r")
    for line in f:
        if line.startswith('*'):
            authors.append(line[1:].strip())
    f.close()
    return authors

def get_long_description():
    f = file("README", "r")
    long_description = f.read()
    f.close()
    long_description.strip()
    return long_description


setup(
    name='PyLucid',
    version=PYLUCID_VERSION_STRING,
    description='PyLucid is an open-source content management system (CMS) using django.',
    long_description = get_long_description(),
    author = get_authors(),
    maintainer = "Jens Diemer",
    url='http://www.pylucid.org',
    packages=find_packages(),
    include_package_data=True, # include package data under svn source control
    zip_safe=False,
#    entry_points={
#        'console_scripts': [
#            'pylucid-admin = pylucid.core.management:execute_from_command_line',
#        ],
#    },
    classifiers = [
        'Development Status :: 1 - Planning',
#        'Development Status :: 2 - Pre-Alpha',
#        'Development Status :: 3 - Alpha',
#        "Development Status :: 4 - Beta",
#        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
#        "Intended Audience :: Education",
#        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Programming Language :: SQL",
        'Framework :: Django',
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ]
)
