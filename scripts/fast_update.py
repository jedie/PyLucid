#!/usr/bin/env python
# coding: utf-8

"""
    fast update src
    ~~~~~~~~~~~~~~~

    fast update all git/svn repositories in the 'src' directory.

    :copyleft: 2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys, os, subprocess


GIT_CMD = "git pull origin"
SVN_CMD = "svn update"


def fast_update(src_path):
    if not os.path.isdir(src_path):
        print "ERROR: Path %r doesn't exist" % src_path
        print "(Please copy this file into e.g.: ~/PyLucid_env/ and call it from there ;)"
        sys.exit(1)

    for dir_item in os.listdir(src_path):
        abs_path = os.path.join(src_path, dir_item)
        if not os.path.isdir(abs_path):
            continue

        if os.path.isdir(os.path.join(abs_path, ".git")):
            shell_command = GIT_CMD
        elif os.path.isdir(os.path.join(abs_path, ".svn")):
            shell_command = SVN_CMD
        else:
            print "Skip %r" % abs_path
            continue

        print "_" * 79
        print "Update '%s' via '%s'..." % (dir_item, shell_command)
        subprocess.call(shell_command, cwd=abs_path, shell=True)
        print


if __name__ == "__main__":
    base_path = os.path.abspath(os.path.dirname(__file__))
    src_path = os.path.join(base_path, "src")

    fast_update(src_path)
