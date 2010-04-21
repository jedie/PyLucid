# coding: utf-8
"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import warnings
import subprocess


__version__ = (0, 9, 0, 'RC2')


VERSION_STRING = '.'.join(str(part) for part in __version__)


try:
    process = subprocess.Popen(
       ["git", "log", "--format='%h'", "-1", "HEAD"],
       stdout = subprocess.PIPE
    )
except Exception, err:
    warnings.warn("Can't get git hash: %s" % err)
else:
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        output = process.stdout.readline().strip().strip("'")
        if len(output) != 7:
            warnings.warn("Can't get git hash, output was: %r" % output)
        else:
            VERSION_STRING += ".git-%s" % output
    else:
        warnings.warn("Can't get git hash, returncode was: %s" % returncode)


if __name__ == "__main__":
    print VERSION_STRING
