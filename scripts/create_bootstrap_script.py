# coding: utf-8

"""
    Create/update the virtualenv bootstrap script BOOTSTRAP_SCRIPT from
    the BOOTSTRAP_SOURCE file.
"""

import sys

try:
    import virtualenv
except ImportError, err:
    print "Import error:", err
    print
    print "Please install virtualenv!"
    print "e.g.: easy_install virtualenv"
    print "More info:"
    print "http://pypi.python.org/pypi/virtualenv"
    print
    sys.exit()


BOOTSTRAP_SCRIPT = "pylucid-boot.py"
BOOTSTRAP_SOURCE = "source-pylucid-boot.py"


def create_bootstrap_script():
    info = "source bootstrap script: %r" % BOOTSTRAP_SOURCE
    print "read", info
    content = "# %s\n" % info
    f = file(BOOTSTRAP_SOURCE, "r")
    content += f.read()
    f.close()

    print "Create/Update %r" % BOOTSTRAP_SCRIPT

    output = virtualenv.create_bootstrap_script(content)

    # Add info lines
    output_lines = output.splitlines()
    output_lines.insert(2, "## Generate with %r" % __file__)
    output_lines.insert(2, "## using: %r" % virtualenv.__file__)
    output = "\n".join(output_lines)
    #print output

    f = file(BOOTSTRAP_SCRIPT, 'w')
    f.write(output)
    f.close()


if __name__ == "__main__":
    create_bootstrap_script()
    print " -- END -- "