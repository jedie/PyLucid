#!/usr/bin/env python
# coding: utf-8

"""
    Check some basic requirements
"""

import sys
import subprocess


class Tester(object):
    def __init__(self):
        self.ok = True

    def check(self, cmd, err_info):
        print " ".join(cmd)
        try:
            returncode = subprocess.call(cmd)
        except Exception, err:
            print "Error:", err
        else:
            if returncode == 0:
                print "OK"
                print
                return

        self.ok = False
        print "***", err_info
        print


if __name__ == "__main__":
    print "requirements pre test (%s)" % __file__
    print

    t = Tester()
    t.check(["python", "-V"], "Python not installed?!?!")
    t.check(["svn", "--version", "--quiet"],
        "Please install subversion! (e.g.: sudo aptitude install subversion)"
    )

    if t.ok == True:
        # All test ok
        sys.exit(0)
    else:
        # One test failed
        sys.exit(-1)

