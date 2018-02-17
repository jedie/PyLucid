#!/usr/bin/python3

"""
    PyLucid Manage CLI
    ~~~~~~~~~~~~~~~~~~

    :created: 08.02.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

__version__ = "0.0.1"

import argparse
import cmd
import logging
import os
import subprocess
import sys

if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)


log = logging.getLogger(__name__)


def verbose_check_call(*args):
    """ 'verbose' version of subprocess.check_output() """
    print("Call: %r" % " ".join(args))
    try:
        subprocess.check_call(args, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise



class PyLucidShell(cmd.Cmd):
    command_alias = {
        "q": "quit",
    }
    intro = 'PyLucid shell.   Type help or ? to list commands.\n'
    prompt = 'PyLucid> '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # e.g.: $ ./pylucid.py upgrade_requirements -> run do_upgrade_requirements() on startup
        self.cmdqueue = sys.argv[1:]

    def do_upgrade_requirements(self, arg):
        """
        run pip-compile for all *.in files

        Direct start with:
            $ ./pylucid.py upgrade_requirements
        """
        for filename in os.listdir("requirements"):
            if not filename.endswith(".in") or filename.startswith("basic"):
                continue
            requirement_in = os.path.join("requirements", filename)
            requirement_out = requirement_in.replace(".in", ".txt")

            print("TODO: %r -> %r" % (requirement_in, requirement_out))
            verbose_check_call("pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in)

    def _install(self, requirements_filename):
        verbose_check_call("pip3", "install", "--upgrade", "pip")
        requirement = os.path.join("requirements", requirements_filename)
        verbose_check_call("pip3", "install", "-r", requirement)

    def do_install_normal(self, arg):
        """
        Install requirements in "normal" mode.
        Requirements file 'normal_installation.txt' will be used.
        Use PyPi packages and read-only sources from github.
        """
        self._install("normal_installation.txt")

    def do_install_developer(self, arg):
        """
        Install requirements in "developer" mode.
        Requirements file 'developer_installation.txt' will be used.

        **only usable for developer with github write access**
        """
        self._install("developer_installation.txt")

    def do_pip_freeze(self, arg):
        "run 'pip freeze': FOO"
        verbose_check_call("pip3", "freeze")

    def do_quit(self, arg):
        "Exit PyLucid shell"
        print("\n\nbye")
        return True

    def precmd(self, line):
        try:
            return self.command_alias[line]
        except KeyError:
            return line

    def postcmd(self, stop, line):
        # stop if we are called with commandline arguments
        if len(sys.argv)>1:
            stop = True
        return stop


if __name__ == '__main__':
    PyLucidShell().cmdloop()
