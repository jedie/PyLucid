#!/usr/bin/env python
# coding: utf-8

"""
    Create/update the virtualenv bootstrap script BOOTSTRAP_SCRIPT from
    the BOOTSTRAP_SOURCE file.
"""

import os
import sys
import pprint
import tempfile
import urllib2

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

def get_pip():
    get_pip_temp = os.path.join(tempfile.gettempdir(), "get-pip.py")
    if os.path.isfile(get_pip_temp):
        print("Use %r" % get_pip_temp)
        with open(get_pip_temp, "r") as f:
            get_pip = f.read()
    else:
        url="https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py"
        print("Request: %r..." % url)
        with open(get_pip_temp, "w") as out_file:
            # Warning: HTTPS requests do not do any verification of the server’s certificate.
            f = urllib2.urlopen(url)
            get_pip = f.read()
            out_file.write(get_pip)

    get_pip_sha = hashlib.sha256(get_pip).hexdigest()
    assert get_pip_sha=="d43dc33a5670d69dd14a9be1f2b2fa27ebf124ec1b212a47425331040f742a9b", \
        "Requested get-pip.py sha256 value is wrong! Hash: %r" % get_pip_sha

    split_index = get_pip.index('if __name__ == "__main__":')
    get_pip = get_pip[:split_index]
    get_pip = get_pip.replace("def main():", "def get_pip():")

    get_pip = "\n# get_pip.py\n" + "\n".join([line for line in get_pip.splitlines() if not line.startswith("#")])

    # print(get_pip)
    return get_pip


def create_bootstrap_script():
    content = "#" * 79

    content += get_pip()

    content += requirements_definitions()

    info = "source bootstrap script: %r" % BOOTSTRAP_SOURCE
    print("read", info)
    content += "\n\n# %s\n" % info
    f = file(BOOTSTRAP_SOURCE, "r")
    content += f.read()
    f.close()

    print "Create/Update %r" % BOOTSTRAP_SCRIPT

    output = virtualenv.create_bootstrap_script(content)

    # Add info lines
    shebang, code = output.split("\n",1)

    f = file(BOOTSTRAP_SCRIPT, 'w')
    f.write(output)
    f.close()


if __name__ == "__main__":
    create_bootstrap_script()
    print(" -- END -- ")
