#!/usr/bin/python3

"""
    PyLucid Boot Admin
    ~~~~~~~~~~~~~~~~~~

    A interactive shell for booting PyLucid.

    Note:
        - This file is "self contained".
        - It used **only** stuff from Python lib.
        - So it's "run able" on a bare python 3 installation
        - On debian / ubuntu the 'python3-venv' package is needed!

    usage, e.g.:

        $ wget https://raw.githubusercontent.com/jedie/PyLucid/pylucid_v3/pylucid/pylucid_boot.py
        $ python3 pylucid_boot.py

        pylucid_boot.py> boot ~/PyLucid_env

    :created: 08.02.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

import cmd
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path

try:
    import venv
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'venv' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)

try:
    import ensurepip
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'ensurepip' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)


__version__ = "0.1.0"


if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)


log = logging.getLogger(__name__)


OWN_FILENAME=Path(__file__).name  # pylucid_boot.py


DEVELOPER_INSTALL=["-e", "git+git@github.com:jedie/PyLucid.git@develop#egg=pylucid"]
NORMAL_INSTALL=[
    # TODO: Remove "--pre" after v3 release
    "--pre", # https://pip.pypa.io/en/stable/reference/pip_install/#pre-release-versions
    "pylucid"
]


def in_virtualenv():
    # Maybe this is not the best way?!?
    return "VIRTUAL_ENV" in os.environ


if in_virtualenv():
    print("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))
else:
    print("We are not in a virtualenv, ok.")


def verbose_check_call(*popenargs, env_updates=None, **kwargs):
    """
    'verbose' version of subprocess.check_output()
    env_updates dict can be used to overwrite os.environ.
    """
    txt = "Call: %r" % " ".join(popenargs)
    if kwargs:
        txt += " with: %s" % repr(kwargs)

    if env_updates is not None:
        txt += " env: %s" % repr(env_updates)
        env=os.environ.copy()
        env.update(env_updates)
        kwargs["env"] = env

    print(txt)

    try:
        subprocess.check_call(popenargs, universal_newlines=True, stderr=subprocess.STDOUT, **kwargs)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise
    print("")


def display_errors(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            return "%s: %s" % (err.__class__.__name__, err)

    return wrapped


class Cmd2(cmd.Cmd):
    """
    Enhanced version of 'Cmd' class:
        - command alias
        - methods can be called directly from commandline: e.g.: ./foobar.py --help
        - Display
    """
    own_filename = OWN_FILENAME
    version = __version__

    command_alias = { # used in self.precmd()
        "q": "quit", "EOF": "quit",
        "--help": "help", "-h": "help", "-?": "help",
    }

    # Will be append to 'doc_leader' in self.do_help():
    complete_hint="\nUse <{key}> to command completion.\n"
    missing_complete="\n(Sorry, no command completion available.)\n" # if 'readline' not available

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.intro = (
            '\n{filename} shell v{version}\n'
            'Type help or ? to list commands.\n'
        ).format(
            filename=self.own_filename,
            version=self.version
        )

        self.prompt = '%s> ' % self.own_filename

        self.doc_leader = (
            "\nHint: All commands can be called directly from commandline.\n"
            "e.g.: $ ./{filename} pip_freeze\n"
        ).format(
            filename=self.own_filename,
        )

        # e.g.: $ pylucid_admin.py boot /tmp/PyLucid-env -> run self.do_boot("/tmp/PyLucid-env") on startup
        args = sys.argv[1:]
        if args:
            self.cmdqueue = [" ".join(args)]

    @display_errors
    def _complete_path(self, text, line, begidx, endidx):
        """
        complete a command argument with a existing path

        usage e.g.:
            class FooCmd(Cmd2):
                def complete_foobar(self, text, line, begidx, endidx):
                    return self._complete_path(text, line, begidx, endidx)

                def do_foobar(self, path): # 'path' is type string!
                    print("path:", path)
        """
        try:
            destination = line.split(" ", 1)[1]
        except IndexError:
            destination = "."

        if destination=="~":
            return [os.sep]

        destination = Path(destination).expanduser().resolve()

        if not destination.is_dir():
            destination = destination.parent.resolve()

        if destination.is_dir():
            complete_list = [x.stem + os.sep for x in destination.iterdir() if x.is_dir()]
            if text:
                if text in complete_list:
                    return [text + os.sep]

                complete_list = [x for x in complete_list if x.startswith(text)]
        else:
            complete_list = []

        return complete_list

    _complete_hint_added=False
    def do_help(self, arg):
        """
        List available commands with "help" or detailed help with "help cmd".
        """
        if not self._complete_hint_added:
            try:
                import readline
            except ImportError:
                self.doc_leader += self.missing_complete
            else:
                self.doc_leader += self.complete_hint.format(key=self.completekey)
            self._complete_hint_added=True

        return super().do_help(arg)

    def do_quit(self, arg):
        "Exit this interactiv shell"
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


class PyLucidEnvBuilder(venv.EnvBuilder):
    verbose = True

    def __init__(self, requirements):
        super().__init__(with_pip=True)
        self.requirements = requirements

    def ensure_directories(self, env_dir):
        print(" * Create the directories for the environment.")
        return super().ensure_directories(env_dir)

    def create_configuration(self, context):
        print(" * Create 'pyvenv.cfg' configuration file.")
        return super().create_configuration(context)

    def setup_python(self, context):
        print(" * Set up a Python executable in the environment.")
        return super().setup_python(context)

    def _setup_pip(self, context):
        print(" * Installs or upgrades pip in a virtual environment.")
        return super()._setup_pip(context)

    def setup_scripts(self, context):
        print(" * Set up scripts into the created environment.")
        return super().setup_scripts(context)

    def post_setup(self, context):
        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.

        :param context: The information for the virtual environment
                        creation request being processed.
        """
        print(" * post-setup modification")

        def call_new_python(*args):
            """
            Do the same as bin/activate so that <args> runs in a "activated" virtualenv.
            """
            verbose_check_call(
                *args,
                env_updates={
                    "VIRTUAL_ENV": context.env_dir,
                    "PATH": "%s:%s" % (context.bin_path, os.environ["PATH"]),
                },
            )

        call_new_python("pip", "install", "--upgrade", "pip")

        # Install PyLucid
        #   in normal mode as package from PyPi
        #   in dev. mode as editable from github
        call_new_python("pip", "install", *self.requirements)

        # Check if ".../bin/pylucid_admin" exists
        pylucid_admin_path = Path(context.bin_path, "pylucid_admin")
        if not pylucid_admin_path.is_file():
            print("ERROR: pylucid_admin not found here: '%s'" % pylucid_admin_path)
            return

        # Install all requirements by call 'pylucid_admin update_env' from installed PyLucid
        call_new_python("pylucid_admin", "update_env")


class PyLucidBootShell(Cmd2):

    #_________________________________________________________________________
    # Normal user commands:

    def _resolve_path(self, path):
        return Path(path).expanduser().resolve()

    def complete_boot(self, text, line, begidx, endidx):
        # print("text: %r" % text)
        # print("line: %r" % line)
        return self._complete_path(text, line, begidx, endidx)

    def _parse_requirements(self, requirement_string):
        requirements = []
        for line in requirement_string.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):

                line = line.split("# ", 1)[0] # Remove pip-compile comments e.g.: "... # via foo"
                line = line.rstrip()

                if line.startswith("-e"): # split editables
                    requirements += line.split(" ")
                else:
                    requirements.append(line)
        return requirements

    def _boot(self, destination, requirements):
        """
        Create a PyLucid virtualenv and install requirements.
        """
        destination = Path(destination).expanduser().resolve()
        if destination.exists():
            self.stdout.write("\nERROR: Path '%s' already exists!\n" % destination)
            return

        self.stdout.write("Create virtualenv: '%s'...\n\n" % destination)

        builder = PyLucidEnvBuilder(requirements)
        builder.create(destination)

        self.stdout.write("\n")

        if not destination.is_dir():
            self.stdout.write("ERROR: Creating virtualenv!\n")
            return
        else:
            self.stdout.write("virtualenv created at: '%s'\n" % destination)

    def do_boot_normal(self, destination):
        """
        "normal" boot PyLucid

        usage:
            > boot_normal [path]

        Create a PyLucid virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/normal_installation.txt)
        """
        self._boot(destination, requirements=NORMAL_INSTALL)
    complete_boot_normal = complete_boot

    def do_boot_developer(self, destination):
        """
        **only usable for developer with github write access**
        (used the requirements/developer_installation.txt)
        """
        self._boot(destination, requirements=DEVELOPER_INSTALL)
    complete_boot_developer = complete_boot


def main():
    PyLucidBootShell().cmdloop()


if __name__ == '__main__':
    main()
