
"""
    PyLucid Normal Admin Shell
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 2018 by Jens Diemer
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys
import time
from pathlib import Path

from pylucid_installer.pylucid_installer import create_instance

# PyLucid
from pylucid.pylucid_boot import Cmd2, VerboseSubprocess
from pylucid.version import __version__

assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip


log = logging.getLogger(__name__)


# Used to check if pip-compiles runs fine, see: PyLucidShell.do_upgrade_requirements()
VERSION_PREFIXES = ("django==1.11.", "django-cms==3.4.")

# Used in PyLucidShell.do_update_env()
PYLUCID_NORMAL_REQ = ["pylucid>=%s" % __version__]

MANAGE_COMMANDS = (  # TODO: Create list dynamicly
    "--help",
    "changepassword",
    "createsuperuser",
    "cms",
    "compress",
    "mtime_cache",
    "check",
    "createcachetable",
    "diffsettings",
    "makemigrations",
    "migrate",
    "sendtestemail",
    "showmigrations",
    "collectstatic",
    "cms_page_info",
    "cms_plugin_info",
    "template_info",
    "image_info",
    "replace_broken",
    "collectstatic",
)


def in_virtualenv():
    # Maybe this is not the best way?!?
    return "VIRTUAL_ENV" in os.environ


class PyLucidNormalShell(Cmd2):
    version = __version__

    def __init__(self, path_helper, *args, **kwargs):
        self.path_helper = path_helper  # bootstrap_env.admin_shell.path_helper.PathHelper instance

        super().__init__(*args, **kwargs)

    def do_create_page_instance(self, arg):
        """
        Create a PyLucid page instance.
        Needs two arguments:
            - destination: filesystem point to create a new instance
            - name: The project name (Should be ASCII without spaces)

        Direct start with:
            $ pylucid_admin create_page_instance [destination] [name]

        tbd.
        """
        try:
            destination, name = arg.split(" ")
        except ValueError as err:
            print("ERROR: %s" % err)
            print("There are two arguments needed: [destination] [name]")
            return

        destination = destination.strip()
        name = name.strip()

        if not destination:
            print("ERROR: destination is needed!")
            return

        if not name:
            print("ERROR: name not given!")
            return

        create_instance(dest=destination, name=name, remove=False, exist_ok=False)

    def test_project_manage(self, *args, timeout=1000, check=False):
        cwd = self.path_helper.base.parent  # e.g.: PyLucid-env/src/pylucid/pylucid_page_instance
        assert cwd.is_dir(), "ERROR: Path not exists: %r" % cwd

        args = ["./pylucid_page_instance/manage.py"] + list(args)

        manage_path = Path(cwd, args[0])
        assert manage_path.is_file(), "ERROR: File not found: '%s'" % manage_path

        return VerboseSubprocess(*args, cwd=str(cwd), timeout=timeout).verbose_call(check=check)

    def complete_test_project_manage(self, text, line, begidx, endidx):
        return self._complete_list(MANAGE_COMMANDS, text, line, begidx, endidx)

    def do_test_project_manage(self, arg):
        """
        call ./manage.py [args] from test project (*not* from your page instance!)

        direct call, e.g.:
        $ pylucid_admin test_project_manage diffsettings
        """
        self.test_project_manage(*arg.split(" "))

    def complete_create_page_instance(self, text, line, begidx, endidx):
        return self._complete_path(text, line, begidx, endidx)

    def do_run_test_project_dev_server(self, arg):
        """
        run django development server with test project

        Direct call:
        $ pylucid_admin run_test_project_dev_server

        Optional arguments are passed to ./manage.py

        (We call pylucid.management.commands.run_test_project_dev_server.Command)
        """
        args = arg.split(" ")

        self.test_project_manage("createcachetable", check=True)

        while True:
            try:
                print("\n")
                print("=" * 79)
                print("=" * 79)
                return_code = self.test_project_manage(
                    "run_test_project_dev_server",
                    *args,
                    timeout=None,  # Run forever
                    check=False,  # Don't sys.exit(return_code) if return_code != 0
                )
                for x in range(3, 0, -1):
                    print("Reload in %i sec..." % x)
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n")
                return  # return back to the cmd loop

    def do_pytest(self, arg):
        """
        Run tests via pytest
        """
        try:
            import pytest
        except ImportError as err:
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)" % err)
        else:
            root_path = str(self.path_helper.base)
            print("chdir %r" % root_path)
            os.chdir(root_path)

            ini = Path(root_path, "pytest.ini")
            assert ini.is_file(), "File not found: %s" % ini

            args = sys.argv[2:]
            print("Call Pytest with args: %s" % repr(args))
            exit_code = pytest.main(args=args)
            sys.exit(exit_code)

    def do_pip_freeze(self, arg):
        """
        Just run 'pip freeze'
        """
        return_code = VerboseSubprocess("pip3", "freeze").verbose_call(check=False)

    def do_update_env(self, arg):
        """
        Update all packages in virtualenv.

        Direct start with:
            $ pylucid_admin update_env

        (Call this command only in a activated virtualenv.)
        """
        if not in_virtualenv():
            self.stdout.write("\nERROR: Only allowed in activated virtualenv!\n\n")
            return

        pip3_path = Path(sys.prefix, "bin", "pip3")
        if not pip3_path.is_file():
            print("ERROR: pip not found here: '%s'" % pip3_path)
            return

        print("pip found here: '%s'" % pip3_path)
        pip3_path = str(pip3_path)

        return_code = VerboseSubprocess(pip3_path, "install", "--upgrade", "pip").verbose_call(check=False)

        # Update the requirements files by...
        if self.path_helper.normal_mode:
            # ... update 'pylucid' PyPi package
            return_code = VerboseSubprocess(pip3_path, "install", "--upgrade", *PYLUCID_NORMAL_REQ).verbose_call(
                check=False
            )
        else:
            # ... git pull pylucid sources
            return_code = VerboseSubprocess("git", "pull", "origin", cwd=str(self.path_helper.pkg_path)).verbose_call(
                check=False
            )

            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".", cwd=str(self.path_helper.pkg_path)
            ).verbose_call(check=False)

        requirement_file_path = str(self.path_helper.req_filepath)

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        return_code = VerboseSubprocess(
            "pip3",
            "install",
            "--exists-action",
            "b",  # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement",
            requirement_file_path,
            timeout=120,  # extended timeout for slow Travis ;)
        ).verbose_call(check=False)

        if not self.path_helper.normal_mode:
            # Run pip-sync only in developer mode
            return_code = VerboseSubprocess(
                "pip-sync", requirement_file_path, cwd=str(self.path_helper.base)
            ).verbose_call(check=False)

            # 'reinstall' pylucid editable, because it's not in 'requirement_file_path':
            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".", cwd=str(self.path_helper.pkg_path)
            ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.self_filename)
        sys.exit(0)
