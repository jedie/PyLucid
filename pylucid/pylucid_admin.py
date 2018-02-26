
import os  # isort:skip

assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip


import logging
import subprocess
import sys
from pathlib import Path

# pylucid.pylucid_boot.in_virtualenv
from pylucid_installer.pylucid_installer import create_instance

# PyLucid
from pylucid.pylucid_boot import Cmd2, in_virtualenv, verbose_check_call
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


SELF_FILEPATH=Path(__file__).resolve()                               # .../src/pylucid/pylucid/pylucid_admin.py
BOOT_FILEPATH=Path(SELF_FILEPATH, "..", "pylucid_boot.py").resolve() # .../src/pylucid/pylucid/pylucid_boot.py
ROOT_PATH=Path(SELF_FILEPATH, "..", "..").resolve()                  # .../src/pylucid/
OWN_FILENAME=SELF_FILEPATH.name                                      # pylucid_admin.py

# print("SELF_FILEPATH: %s" % SELF_FILEPATH)
# print("BOOT_FILEPATH: %s" % BOOT_FILEPATH)
# print("ROOT_PATH: %s" % ROOT_PATH)
# print("OWN_FILENAME: %s" % OWN_FILENAME)


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
        src_path = Path(sys.prefix, "src", "pylucid")
        if src_path.is_dir():
            print("PyLucid is installed as editable here: %s" % src_path)
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

    def complete_create_page_instance(self, text, line, begidx, endidx):
        return self._complete_path(text, line, begidx, endidx)

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

        print("TODO: Create instance with name %r at: %r" % (name, destination))
        create_instance(dest=destination, name=name, remove=False, exist_ok=False)

    def do_pytest(self, arg):
        """
        Run tests via pytest
        """
        try:
            import pytest
        except ImportError as err:
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)")
        else:
            pytest.main()

    def do_pip_freeze(self, arg):
        """
        Just run 'pip freeze'
        """
        verbose_check_call("pip3", "freeze")

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

        verbose_check_call(pip3_path, "install", "--upgrade", "pip")

        req = Requirements()

        # Update the requirements files by...
        if req.normal_mode:
            # ... update 'pylucid' PyPi package
            verbose_check_call(pip3_path, "install", "--upgrade", PYLUCID_NORMAL_REQ)
        else:
            # ... git pull pylucid sources
            verbose_check_call("git", "pull", "origin", cwd=ROOT_PATH)
            verbose_check_call(pip3_path, "install", "--editable", ".", cwd=ROOT_PATH)

        requirement_file_path = str(req.get_requirement_file_path())

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        verbose_check_call(
            "pip3", "install",
            "--exists-action", "b", # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement", requirement_file_path
        )

        if not req.normal_mode:
            # Run pip-sync only in developer mode
            verbose_check_call("pip-sync", requirement_file_path, cwd=ROOT_PATH)

            # 'reinstall' pylucid editable, because it's not in 'requirement_file_path':
            verbose_check_call(pip3_path, "install", "--editable", ".", cwd=ROOT_PATH)

        self.stdout.write("Please restart %s\n" % self.own_filename)
        sys.exit(0)

    #_________________________________________________________________________
    # Developer commands:

    def do_upgrade_requirements(self, arg):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.
        3. insert requirement content into pylucid_admin.py

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

            verbose_check_call(
                "pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in,
                cwd=requirements_path
            )

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
                self.stdout.write(line)
                self.stdout.flush()
                output.append("# %s" % line)

            self.stdout.write("\nUpdate file %r\n" % requirement_out)
            filepath = Path(requirements_path, requirement_out).resolve()
            assert filepath.is_file(), "File not exists: %r" % filepath
            with open(filepath, "a") as f:
                f.writelines(output)


def main():
    PyLucidShell().cmdloop()


if __name__ == '__main__':
    main()
