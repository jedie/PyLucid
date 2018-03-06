
import os  # isort:skip
import re

assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip


import logging
import subprocess
import sys
import time
from pathlib import Path

# pylucid.pylucid_boot.in_virtualenv
from pylucid_installer.pylucid_installer import create_instance

# PyLucid
from pylucid.pylucid_boot import Cmd2, VerboseSubprocess
from pylucid.version import __version__


log = logging.getLogger(__name__)


# Used to check if pip-compiles runs fine, see: PyLucidShell.do_upgrade_requirements()
VERSION_PREFIXES = (
    "django==1.11.",
    "django-cms==3.4.",
)

# Used in PyLucidShell.do_update_env()
PYLUCID_NORMAL_REQ=[
    # TODO: Remove "--pre" after v3 release
    "--pre", # https://pip.pypa.io/en/stable/reference/pip_install/#pre-release-versions
    "pylucid>=%s" % __version__
]

MANAGE_COMMANDS=( # TODO: Create list dynamicly
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

SELF_FILEPATH=Path(__file__).resolve()                               # .../src/pylucid/pylucid/pylucid_admin.py
BOOT_FILEPATH=Path(SELF_FILEPATH, "..", "pylucid_boot.py").resolve() # .../src/pylucid/pylucid/pylucid_boot.py
ROOT_PATH=Path(SELF_FILEPATH, "..", "..").resolve()                  # .../src/pylucid/
OWN_FILENAME=SELF_FILEPATH.name                                      # pylucid_admin.py

# print("SELF_FILEPATH: %s" % SELF_FILEPATH)
# print("BOOT_FILEPATH: %s" % BOOT_FILEPATH)
# print("ROOT_PATH: %s" % ROOT_PATH)
# print("OWN_FILENAME: %s" % OWN_FILENAME)


def in_virtualenv():
    # Maybe this is not the best way?!?
    return "VIRTUAL_ENV" in os.environ


if in_virtualenv():
    print("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))
else:
    print("We are not in a virtualenv, ok.")


def iter_subprocess_output(*popenargs, **kwargs):
    """
    A subprocess with tee ;)
    """
    print("Call: %s" % " ".join(popenargs))

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"]="1" # If a python script called ;)

    proc=subprocess.Popen(popenargs,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=1, env=env, universal_newlines=True,
        **kwargs
    )
    return iter(proc.stdout.readline,'')


class Requirements:
    DEVELOPER_INSTALL="developer"
    NORMAL_INSTALL="normal"
    REQUIREMENTS = {
        DEVELOPER_INSTALL: "developer_installation.txt",
        NORMAL_INSTALL: "normal_installation.txt",
    }
    def __init__(self):
        self.src_path = Path(sys.prefix, "src")
        src_pylucid_path = Path(self.src_path, "pylucid")
        if src_pylucid_path.is_dir():
            print("PyLucid is installed as editable here: %s" % src_pylucid_path)
            self.install_mode=self.DEVELOPER_INSTALL
        else:
            print("PyLucid is installed as packages here: %s" % ROOT_PATH)
            self.install_mode=self.NORMAL_INSTALL

    @property
    def normal_mode(self):
        return self.install_mode == self.NORMAL_INSTALL

    def get_requirement_path(self):
        """
        :return: Path(.../pylucid/requirements/)
        """
        requirement_path = Path(ROOT_PATH, "pylucid", "requirements").resolve()
        if not requirement_path.is_dir():
            raise RuntimeError("Requirements directory not found here: %s" % requirement_path)
        return requirement_path

    def get_requirement_file_path(self):
        """
        :return: Path(.../pylucid/requirements/<mode>_installation.txt)
        """
        requirement_path = self.get_requirement_path()
        filename = self.REQUIREMENTS[self.install_mode]

        requirement_file_path = Path(requirement_path, filename).resolve()
        if not requirement_file_path.is_file():
            raise RuntimeError("Requirements file not found here: %s" % requirement_file_path)

        return requirement_file_path



class PyLucidShell(Cmd2):
    own_filename = OWN_FILENAME
    version = __version__

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
        cwd = Path(ROOT_PATH, "pylucid_page_instance")
        assert cwd.is_dir(), "ERROR: Path not exists: %r" % cwd

        args=["./manage.py"] + list(args)

        manage_path = Path(cwd, args[0])
        assert manage_path.is_file(), "ERROR: File not found: '%s'" % manage_path

        return VerboseSubprocess(*args, cwd=cwd, timeout=timeout).verbose_call(check=check)

    def complete_test_project_manage(self, text, line, begidx, endidx):
        return self._complete_list(MANAGE_COMMANDS, text, line, begidx, endidx)

    def do_test_project_manage(self, arg):
        """
        call ./manage.py [args] from test project (*not* from your page instance!)

        direct call, e.g.:
        $ ./admin.py test_project_manage diffsettings
        """
        self.test_project_manage(*arg.split(" "))

    def complete_create_page_instance(self, text, line, begidx, endidx):
        return self._complete_path(text, line, begidx, endidx)

    def do_run_test_project_dev_server(self, arg):
        """
        run django development server with test project

        Direct call:
        $ ./pylucid_admin.py run_test_project_dev_server

        Optional arguments are passed to ./manage.py

        (We call pylucid.management.commands.run_test_project_dev_server.Command)
        """
        args = arg.split(" ")

        self.test_project_manage("createcachetable", check=True)

        while True:
            try:
                print("\n")
                print("="*79)
                print("="*79)
                return_code = self.test_project_manage(
                    "run_test_project_dev_server",
                    *args,
                    timeout=None, # Run forever
                    check=False, # Don't sys.exit(return_code) if return_code != 0
                )
                for x in range(3,0,-1):
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
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)")
        else:
            root_path = str(ROOT_PATH)
            print("chdir %r" % root_path)
            os.chdir(root_path)

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

        return_code = VerboseSubprocess(
            pip3_path, "install", "--upgrade", "pip"
        ).verbose_call(check=False)

        req = Requirements()

        # Update the requirements files by...
        if req.normal_mode:
            # ... update 'pylucid' PyPi package
            return_code = VerboseSubprocess(
                pip3_path, "install", "--upgrade", *PYLUCID_NORMAL_REQ
            ).verbose_call(check=False)
        else:
            # ... git pull pylucid sources
            return_code = VerboseSubprocess(
                "git", "pull", "origin",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

        requirement_file_path = str(req.get_requirement_file_path())

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        return_code = VerboseSubprocess(
            "pip3", "install",
            "--exists-action", "b", # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement", requirement_file_path,
            timeout=120  # extended timeout for slow Travis ;)
        ).verbose_call(check=False)

        if not req.normal_mode:
            # Run pip-sync only in developer mode
            return_code = VerboseSubprocess(
                "pip-sync", requirement_file_path,
                cwd=ROOT_PATH
            ).verbose_call(check=False)

            # 'reinstall' pylucid editable, because it's not in 'requirement_file_path':
            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.own_filename)
        sys.exit(0)

    #_________________________________________________________________________
    # Developer commands:

    def do_upgrade_requirements(self, arg):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.

        Direct start with:
            $ pylucid_admin upgrade_requirements
        """
        assert BOOT_FILEPATH.is_file(), "Bootfile not found here: %s" % BOOT_FILEPATH

        req = Requirements()
        requirements_path = req.get_requirement_path()

        for requirement_in in requirements_path.glob("*.in"):
            requirement_in = Path(requirement_in).name

            if requirement_in.startswith("basic_"):
                continue

            requirement_out = requirement_in.replace(".in", ".txt")

            self.stdout.write("_"*79 + "\n")

            # We run pip-compile in ./requirements/ and add only the filenames as arguments
            # So pip-compile add no path to comments ;)

            return_code = VerboseSubprocess(
                "pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in,
                cwd=requirements_path
            ).verbose_call(check=True)

            if not requirement_in.startswith("test_"):
                req_out = Path(requirements_path, requirement_out)
                with req_out.open("r") as f:
                    requirement_out_content = f.read()

                for version_prefix in VERSION_PREFIXES:
                    if not version_prefix in requirement_out_content:
                        raise RuntimeError("ERROR: %r not found!" % version_prefix)

            self.stdout.write("_"*79 + "\n")
            output = [
                "\n#\n# list of out of date packages made with piprot:\n#\n"
            ]
            for line in iter_subprocess_output("piprot", "--outdated", requirement_out, cwd=requirements_path):
                print(line, flush=True)
                output.append("# %s" % line)

            self.stdout.write("\nUpdate file %r\n" % requirement_out)
            filepath = Path(requirements_path, requirement_out).resolve()
            assert filepath.is_file(), "File not exists: %r" % filepath
            with open(filepath, "a") as f:
                f.writelines(output)

    def do_change_editable_address(self, arg):
        """
        Replace git remote url from github read-only 'https' to 'git@'
        e.g.:

        OLD: https://github.com/jedie/PyLucid.git
        NEW: git@github.com:jedie/PyLucid.git

        **This is only developer with github write access ;)**

        git remote set-url origin https://github.com/jedie/python-creole.git

        Direct start with:
            $ pylucid_admin change_editable_address
        """
        req = Requirements()
        if req.normal_mode:
            print("ERROR: Only available in 'developer' mode!")
            return

        src_path = req.src_path  # Path instance pointed to 'src' directory
        for p in src_path.iterdir():
            if not p.is_dir():
                continue

            if str(p).endswith(".bak"):
                continue

            print("\n")
            print("*"*79)
            print("Change: %s..." % p)

            try:
                output = VerboseSubprocess(
                    "git", "remote", "-v",
                    cwd=str(p),
                ).verbose_output(check=False)
            except subprocess.CalledProcessError:
                print("Skip.")
                continue

            (name, url) = re.findall("(\w+?)\s+([^\s]*?)\s+", output)[0]
            print("Change %r url: %r" % (name, url))

            new_url=url.replace("https://github.com/", "git@github.com:")
            if new_url == url:
                print("ERROR: url not changed!")
                continue

            VerboseSubprocess("git", "remote", "set-url", name, new_url, cwd=str(p)).verbose_call(check=False)
            VerboseSubprocess("git", "remote", "-v", cwd=str(p)).verbose_call(check=False)


def main():
    PyLucidShell().cmdloop()


if __name__ == '__main__':
    main()
