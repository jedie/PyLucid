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


def get_authors():
    try:
        f = file(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r")
        authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
        f.close()
    except Exception, err:
        authors = "[Error: %s]" % err
    return authors


def get_long_description():
    """
    returns README.creole as ReStructuredText.
    Code from:
        https://code.google.com/p/python-creole/wiki/UseInSetup
    """
    desc_creole = ""
    raise_errors = "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv
    try:
        f = file(os.path.join(PACKAGE_ROOT, "README.creole"), "r")
        desc_creole = f.read()
        f.close()
        desc_creole = unicode(desc_creole, 'utf-8').strip()

        try:
            from creole import creole2html, html2rest
        except ImportError:
            etype, evalue, etb = sys.exc_info()
            evalue = etype("%s - Please install python-creole, e.g.: pip install python-creole" % evalue)
            raise etype, evalue, etb

        desc_html = creole2html(desc_creole)
        long_description = html2rest(desc_html)
        long_description = long_description.encode("utf-8")
    except Exception, err:
        if raise_errors:
            raise
        # Don't raise the error e.g. in ./setup install process
        long_description = "[Error: %s]\n%s" % (err, desc_creole)

    if raise_errors:
        # Try if created ReSt code can be convertet into html
        from creole.rest2html.clean_writer import rest2html
        rest2html(long_description)

    return long_description


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
    long_description=get_long_description(),
    author=get_authors(),
    maintainer="Jens Diemer",
    url='http://www.pylucid.org',
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
