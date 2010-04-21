#!/usr/bin/env python
# coding: utf-8

"""
    Check some basic requirements
"""

import sys
import subprocess


def check(cmd, err_info):
    print "run '%s':" % " ".join(cmd)
    try:
        returncode = subprocess.call(cmd)
    except Exception, err:
        print "Error:", err
    else:
        if returncode == 0:
            print
            return True

    print "***", err_info
    print
    return False


if __name__ == "__main__":
    print "requirements pre test (%s)" % __file__
    print

    python_exists = check(["python", "-V"], "Python not installed?!?!")
    svn_exists = check(["svn", "--version", "--quiet"],
        "Please install subversion!\n"
        "e.g.: sudo aptitude install subversion"
    )
    check(["git", "--version"],
        "Please install git, if you want to use it.\n"
        "e.g.: sudo aptitude install git-core"
        "You can use github svn gateway without git!"
    )

    if python_exists and svn_exists:
        # All test ok
        sys.exit(0)
    else:
        # One test failed
        sys.exit(-1)

