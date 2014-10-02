#!/usr/bin/env python
# coding: utf-8

"""
    Create/update the virtualenv bootstrap script BOOTSTRAP_SCRIPT from
    the BOOTSTRAP_SOURCE file.
"""

from __future__ import absolute_import, division, print_function

import os
import sys
import pprint

try:
    import virtualenv
except ImportError as err:
    print("Import error:", err)
    print()
    print("Please install virtualenv!")
    print("e.g.: easy_install virtualenv")
    print("More info:")
    print("http://pypi.python.org/pypi/virtualenv")
    print()
    sys.exit(-1)

try:
    import pylucid_project
except ImportError as err:
    print("Import error:", err)
    print()
    print("Not running in activated virtualenv?")
    print()
    sys.exit(-1)


PYLUCID_BASE_PATH = os.path.abspath(os.path.dirname(pylucid_project.__file__))

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOTSTRAP_SCRIPT = os.path.join(ROOT, "pylucid-boot.py")
BOOTSTRAP_SOURCE = os.path.join(ROOT, "source-pylucid-boot.py")


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


def create_bootstrap_script():
    content = ""

    content += requirements_definitions()

    info = "source bootstrap script: %r" % BOOTSTRAP_SOURCE
    print("read", info)
    content += "\n\n# %s\n" % info
    with open(BOOTSTRAP_SOURCE, "r") as f:
        content += f.read()

    print("Create/Update %r" % BOOTSTRAP_SCRIPT)

    output = virtualenv.create_bootstrap_script(content)

    # Add info lines
    shebang, code = output.split("\n",1)

    generator_filepath = os.path.abspath(__file__)
    pos = generator_filepath.index(os.sep + "PyLucid" + os.sep)
    generator_filepath=generator_filepath[pos:]

    info_line = "\n".join([
        "## Generated with %r" % generator_filepath,
        "## using: %r v%s" % (virtualenv.__file__, virtualenv.virtualenv_version),
        "## python v%s" % sys.version.replace("\n", " "),
    ])


    output = "\n\n".join([
        shebang,
        info_line,
        "from __future__ import absolute_import, division, print_function",
        code,
    ])
    # print(output)

    with open(BOOTSTRAP_SCRIPT, 'w') as f:
        f.write(output)


if __name__ == "__main__":
    create_bootstrap_script()
    print(" -- END -- ")
