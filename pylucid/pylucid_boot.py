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

import sys  # isort:skip
if sys.version_info < (3, 5):  # isort:skip
    print("\nERROR: Python 3.5 or greater is required!")
    print("(Current Python Verison is %s)\n" % sys.version.split(" ",1)[0])
    sys.exit(101)

import cmd
import logging
import os
import subprocess
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


__version__ = "0.2.0"


log = logging.getLogger(__name__)

# Note:
#   on 'master' branch: '--pre' flag must not be set: So the last release on PyPi will be installed.
#   on 'develop' branch: set the '--pre' flag and publish 'preview' versions on PyPi.
#
DEVELOPER_INSTALL=["-e", "git+https://github.com/jedie/PyLucid.git@master#egg=pylucid"]
NORMAL_INSTALL=[
    # "--pre", # https://pip.pypa.io/en/stable/reference/pip_install/#pre-release-versions
    "pylucid"
]

OWN_FILENAME=Path(__file__).name  # pylucid_boot.py

SUBPROCESS_TIMEOUT=60  # default timeout for subprocess calls


class VerboseSubprocess:
    """
    Verbose Subprocess
    """
    def __init__(self, *popenargs, env_updates=None, timeout=SUBPROCESS_TIMEOUT, universal_newlines=True, **kwargs):
        """
        :param popenargs: 'args' for subprocess.Popen()
        :param env_updates: dict to overwrite os.environ.
        :param timeout: pass to subprocess.Popen()
        :param kwargs: pass to subprocess.Popen()
        """
        self.popenargs = popenargs
        self.kwargs = kwargs

        self.kwargs["timeout"] = timeout
        self.kwargs["universal_newlines"] = universal_newlines

        self.args_str = " ".join([str(x) for x in self.popenargs])
        self.txt = "Call: %r" % self.args_str
        kwargs_txt=[]
        for key, value in self.kwargs.items():
            kwargs_txt.append("%s=%s" % (key, value))
        self.txt += " with: %s" % ", ".join(kwargs_txt)

        if env_updates is not None:
            self.txt += " env: %s" % repr(env_updates)
            env=os.environ.copy()
            env.update(env_updates)
            self.kwargs["env"] = env

    def print_call_info(self):
        print("")
        print("_"*79)
        print(self.txt)
        print("", flush=True)

    def print_exit_code(self, exit_code):
        print("\nExit code %r from %r\n" % (exit_code, self.args_str), flush=True)

    def verbose_call(self, check=True):
        """
        run subprocess.call()

        :param check: if True and subprocess exit_code !=0: sys.exit(exit_code) after run.
        :return: process exit code
        """
        self.print_call_info()

        try:
            exit_code = subprocess.call(self.popenargs, stderr=subprocess.STDOUT, **self.kwargs)
        except KeyboardInterrupt:
            print("\nExit %r\n" % self.args_str, flush=True)
            exit_code=None # good idea?!?

        sys.stderr.flush()

        self.print_exit_code(exit_code)
        if check and exit_code:
            sys.exit(exit_code)

        return exit_code

    def verbose_output(self, check=True):
        """
        run subprocess.check_output()

        :param check: if True and subprocess exit_code !=0: sys.exit(exit_code) after run.
        :return: process output
        """
        self.print_call_info()

        try:
            return subprocess.check_output(self.popenargs, **self.kwargs)
        except subprocess.CalledProcessError as err:
            print("\n%s" % err)
            if check:
                sys.exit(err.returncode)
            raise


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
        "": "help", # If user just send a ENTER ;)
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
            "e.g.: $ ./{filename} help\n"
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

        def call_new_python(*args, **kwargs):
            """
            Do the same as bin/activate so that <args> runs in a "activated" virtualenv.
            """
            kwargs.update({
                "env_updates": {
                    "VIRTUAL_ENV": context.env_dir,
                    "PATH": "%s:%s" % (context.bin_path, os.environ["PATH"]),
                }
            })
            VerboseSubprocess(*args, **kwargs).verbose_call(
                check=True # sys.exit(return_code) if return_code != 0
            )

        call_new_python("pip", "install", "--upgrade", "pip")

        # Install PyLucid
        #   in normal mode as package from PyPi
        #   in dev. mode as editable from github
        call_new_python(
            "pip", "install",
            # "--verbose",
            *self.requirements
        )

        # Check if ".../bin/pylucid_admin" exists
        pylucid_admin_path = Path(context.bin_path, "pylucid_admin")
        if not pylucid_admin_path.is_file():
            print("ERROR: pylucid_admin not found here: '%s'" % pylucid_admin_path)
            VerboseSubprocess("ls", "-la", str(context.bin_path)).verbose_call()
            sys.exit(-1)

        # Install all requirements by call 'pylucid_admin update_env' from installed PyLucid
        call_new_python("pylucid_admin", "update_env", timeout=240)  # extended timeout for slow Travis ;)


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
        destination = Path(destination).expanduser()
        if destination.exists():
            self.stdout.write("\nERROR: Path '%s' already exists!\n" % destination)
            sys.exit(1)

        self.stdout.write("Create virtualenv: '%s'...\n\n" % destination)

        builder = PyLucidEnvBuilder(requirements)
        builder.create(str(destination))

        self.stdout.write("\n")

        if not destination.is_dir():
            self.stdout.write("ERROR: Creating virtualenv!\n")
            sys.exit(1)
        else:
            self.stdout.write("virtualenv created at: '%s'\n" % destination)

    def do_boot(self, destination):
        """
        bootstrap PyLucid virtualenv in "normal" mode.

        usage:
            > boot [path]

        Create a PyLucid virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/normal_installation.txt)
        """
        self._boot(destination, requirements=NORMAL_INSTALL)
    complete_boot = complete_boot

    def do_boot_developer(self, destination):
        """
        bootstrap PyLucid virtualenv in "developer" mode:
        All own projects installed as editables via github HTTPS (readonly)

        **Should be only used for developing/contributing. All others: Use normal 'boot' ;) **

        usage:
            > boot_developer [path]

        Create a PyLucid virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/developer_installation.txt)
        """
        self._boot(destination, requirements=DEVELOPER_INSTALL)
    complete_boot_developer = complete_boot


def main():
    PyLucidBootShell().cmdloop()


if __name__ == '__main__':
    main()
