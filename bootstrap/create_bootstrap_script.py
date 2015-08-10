#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid bootstrap creation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Create/update the virtualenv bootstrap script BOOTSTRAP_SCRIPT from
    the BOOTSTRAP_SOURCE file.

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import sys
import pprint

try:
    import virtualenv
except ImportError as err:
    print("Import error: %s\n" % err)
    print("Please install virtualenv!")
    print("e.g.: easy_install virtualenv")
    print("More info:")
    print("\thttp://pypi.python.org/pypi/virtualenv\n")
    sys.exit(-1)

# https://github.com/jedie/bootstrap_env
from bootstrap_env.generate_bootstrap import generate_bootstrap
from bootstrap_env.utils.sourcecode_utils import get_code

try:
    import pylucid_project
except ImportError as err:
    print("Import error: %s\n" % err)
    print("Maybe, not running in activated virtualenv?\n")
    sys.exit(-1)


CUT_MARK="# --- CUT here ---"

PYLUCID_BASE_PATH = os.path.abspath(os.path.dirname(pylucid_project.__file__))
print("PyLucid base path: %r" % PYLUCID_BASE_PATH)

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOTSTRAP_SCRIPT = os.path.normpath(os.path.join(ROOT, "pylucid-boot.py"))

SOURCE_PATH=os.path.join(ROOT, "sources")

PREFIX_SCRIPT = os.path.join(SOURCE_PATH, "prefix_code.py")

EXTEND_PARSER_SCRIPT = os.path.join(SOURCE_PATH, "extend_parser.py")
ADJUST_OPTIONS_SCRIPT = os.path.join(SOURCE_PATH, "adjust_options.py")
AFTER_INSTALL_SCRIPT = os.path.join(SOURCE_PATH, "after_install.py")



def parse_requirements(filename):
    filepath = os.path.join(PYLUCID_BASE_PATH, "../requirements", filename)
    with open(filepath, "r") as f:
        entries = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-r"):
                recursive_filename = line.split("-r ")[1]
                entries += parse_requirements(recursive_filename)
                continue
            if line.startswith("-e"):
                url = line.split("-e ")[1]
                entries.append("--editable=%s" % url)
            else:
                entries.append(line)

    return entries

def requirements_definitions():
    content = []
    for filename in ("normal_installation.txt", "developer_installation.txt"):
        content.append("\n# requirements from %s" % filename)
        requirements_list = parse_requirements(filename)

        req_type = os.path.splitext(filename)[0].upper()
        content.append(
            "%s = %s" % (req_type, pprint.pformat(requirements_list))
        )

    return "\n".join(content)


if __name__ == '__main__':
    prefix_code = "\n".join([
        requirements_definitions(),
        get_code(PREFIX_SCRIPT, CUT_MARK),
    ])

    # print(additional_code)

    generate_bootstrap(
        out_filename=BOOTSTRAP_SCRIPT,
        add_extend_parser=EXTEND_PARSER_SCRIPT,
        add_adjust_options=ADJUST_OPTIONS_SCRIPT,
        add_after_install=AFTER_INSTALL_SCRIPT,
        cut_mark=CUT_MARK,
        prefix=prefix_code,
        suffix=None,
    )