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

    def do_upgrade_requirements(self, arg):
        "Update version information in requirements.txt via pip-compile"
        print("TODO: upgrade_requirements")

    def complete_install_requirements(self, text, *args):
        items = ["normal", "developer"]
        for item in items:
            if item.startswith(text):
                return [item]
        return items

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


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))

if __name__ == '__main__':
    PyLucidShell().cmdloop()
