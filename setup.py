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

from pylucid_project import VERSION_STRING


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_authors():
    f = file(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r")
    authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
    f.close()
    return authors


def get_long_description():
    f = file(os.path.join(PACKAGE_ROOT, "README"), "r")
    long_description = f.read().strip()
    f.close()
    return long_description



setup(
    name='PyLucid',
    version=VERSION_STRING,
    description='PyLucid is an open-source web content management system (CMS) using django.',
    long_description=get_long_description(),
    author=get_authors(),
    maintainer="Jens Diemer",
    url='http://www.pylucid.org',
    packages=find_packages(
        exclude=[".project", ".pydevproject", "pylucid_project.external_plugins.*"]
    ),
    include_package_data=True, # include package data under svn source control
    zip_safe=False,
    classifiers=[
#        'Development Status :: 1 - Planning',
#        'Development Status :: 2 - Pre-Alpha',
#        'Development Status :: 3 - Alpha',
        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
#        "Intended Audience :: Education",
#        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        'Framework :: Django',
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ]
)
