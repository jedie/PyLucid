#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid distutils setup
    ~~~~~~~~~~~~~~~~~~~~~~~

    FIXME!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE for more details.
"""

import os, sys

from distutils.core import setup

sys.path.insert(0, os.path.join(os.getcwd(), "pylucid"))

from PyLucid import PYLUCID_VERSION_STRING

def get_authors():
    authors = []
    f = file("AUTHORS", "r")
    for line in f:
        if line.startswith('*'):
            authors.append(line[1:].strip())
    f.close()
    return authors

f = file("README", "r")
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name = "PyLucid",
    version = PYLUCID_VERSION_STRING,
    url = 'http://www.pylucid.org/',
    download_url = "http://sourceforge.net/project/showfiles.php?group_id=146328",
    author = get_authors(),
    maintainer = "Jens Diemer",
    description = 'A CMS written in PyLucid using django.',
    long_description = LONG_DESCRIPTION,
    keywords = 'cms django wsgi web',
    platforms = 'any',
#    zip_safe = False,
#    include_package_data = True,
    scripts = ["pylucid/django-admin.sh", "pylucid/standalone_linux.sh"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: TurboGears",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: German",
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Programming Language :: SQL",
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ]
)