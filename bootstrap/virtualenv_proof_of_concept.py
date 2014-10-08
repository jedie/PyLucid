#!/usr/bin/env python
# coding: utf-8

import hashlib
import os
import sys
import tempfile
import urllib2
import virtualenv

GET_PIP_URL="https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py"
GET_PIP_SHA256="d43dc33a5670d69dd14a9be1f2b2fa27ebf124ec1b212a47425331040f742a9b"

BASE_CODE="""
##############################################################
# base code:

def extend_parser(parser):
    sys.stdout.write("extend_parser called.\\n")

def adjust_options(options, args):
    sys.stdout.write("adjust_options args: %r\\n" % args)

def after_install(options, home_dir):
    sys.stdout.write("after_install from %r\\n" % home_dir)

##############################################################
"""


def get_pip():
    get_pip_temp = os.path.join(tempfile.gettempdir(), "get-pip.py")
    if os.path.isfile(get_pip_temp):
        print("Use %r" % get_pip_temp)
        with open(get_pip_temp, "r") as f:
            get_pip = f.read()
    else:
        print("Request: %r..." % GET_PIP_URL)
        with open(get_pip_temp, "w") as out_file:
            # Warning: HTTPS requests do not do any verification of the server's certificate.
            f = urllib2.urlopen(GET_PIP_URL)
            get_pip = f.read()
            out_file.write(get_pip)

    get_pip_sha = hashlib.sha256(get_pip).hexdigest()
    assert get_pip_sha==GET_PIP_SHA256, "Requested get-pip.py sha256 value is wrong! SHA256 is: %r" % get_pip_sha

    split_index = get_pip.index('if __name__ == "__main__":')
    get_pip = get_pip[:split_index]
    get_pip = get_pip.replace("def main():", "def get_pip():")

    get_pip = "\n# get_pip.py\n" + "\n".join([line for line in get_pip.splitlines() if not line.startswith("#")])

    # print(get_pip)
    return get_pip


def create_bootstrap(out_filename, code):
    with open(out_filename, 'w') as f:
        f.write(virtualenv.create_bootstrap_script(code))

    print("%r written." % out_filename)


if __name__ == '__main__':
    code = "\n".join([
        "## Generated using: %r v%s" % (virtualenv.__file__, virtualenv.virtualenv_version),
        "## Python v%s" % sys.version.replace("\n", " "),
    ])
    code += BASE_CODE
    code += get_pip()

    out_filename="created-test-bootstrap.py"
    create_bootstrap(out_filename, code)

