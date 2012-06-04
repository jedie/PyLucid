#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid distutils setup
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Links
    ~~~~~
    
    http://www.python-forum.de/viewtopic.php?f=21&t=26895 (de)

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from setuptools import setup, find_packages

from pylucid_project import VERSION_STRING


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


# convert creole to ReSt on-the-fly, see also:
# https://code.google.com/p/python-creole/wiki/UseInSetup
try:
    from creole.setup_utils import get_long_description
except ImportError:
    if "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("%s - Please install python-creole >= v0.8 -  e.g.: pip install python-creole" % evalue)
        raise etype, evalue, etb
    long_description = None
else:
    long_description = get_long_description(PACKAGE_ROOT)


def get_authors():
    try:
        f = file(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r")
        authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
        f.close()
    except Exception, err:
        authors = "[Error: %s]" % err
    return authors


def get_install_requires():
    def parse_requirements(filename):
        filepath = os.path.join(PACKAGE_ROOT, "requirements", filename)
        f = file(filepath, "r")
        entries = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            if line.startswith("-e "):
                line = line.split("#egg=")[1]
            if line.lower() == "pylucid":
                continue
            entries.append(line)
        f.close()
        return entries

    requirements = []
    requirements += parse_requirements("basic_requirements.txt")
    requirements += parse_requirements("normal_installation.txt")
    return requirements


setup_info = dict(
    name='PyLucid',
    version=VERSION_STRING,
    description='PyLucid is an open-source web content management system (CMS) using django.',
    long_description=long_description,
    author=get_authors(),
    maintainer="Jens Diemer",
    url='http://www.pylucid.org',
    download_url = 'http://www.pylucid.org/en/download/',
    packages=find_packages(
        exclude=[".project", ".pydevproject", "pylucid_project.external_plugins.*"]
    ),
    include_package_data=True, # include package data under version control
    install_requires=get_install_requires(),
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
setup(**setup_info)
