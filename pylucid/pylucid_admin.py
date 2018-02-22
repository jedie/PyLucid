
import os  # isort:skip

# pylucid.pylucid_boot.in_virtualenv
assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip


import glob
import logging
import re
import subprocess
import sys
from pathlib import Path

# PyLucid
from pylucid.pylucid_boot import Cmd2, in_virtualenv, verbose_check_call

log = logging.getLogger(__name__)


__version__ = "0.0.1"


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


class PyLucidShell(Cmd2):
    own_filename = OWN_FILENAME

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

        src_requirement_path = Path(sys.prefix, "src", "pylucid", "requirements", "developer_installation.txt")
        src_requirement_path = src_requirement_path.resolve()
        if src_requirement_path.is_file():
            self.stdout.write("Use: '%s'\n" % src_requirement_path)
            verbose_check_call(
                "pip3", "install",
                "--exists-action", "b", # action when a path already exists: (b)ackup
                "--upgrade",
                "--requirement", str(src_requirement_path)
            )
        else:
            self.stdout.write("(No developer installation: File doesn't exists: '%s')" % src_requirement_path)
            # TODO: Implement "normal" update!
            # Maybe, something like this:
            #
            #       pip3 install -U pip
            #       pip3 install -U pylucid
            #       pylucid_admin update_env stage2
            #
            self.stdout.write("TODO!")
            return

        self.stdout.write("Please restart %s" % self.own_filename)
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

        requirements_path = Path(ROOT_PATH, "requirements").resolve()
        assert requirements_path.is_dir(), "Path doesn't exists: %r" % requirements_path

        for requirement_in in glob.glob(os.path.join(ROOT_PATH, "requirements", "*.in")):
            if "basic_" in requirement_in:
                continue

            requirement_in = Path(requirement_in).name
            requirement_out = requirement_in.replace(".in", ".txt")

            self.stdout.write("_"*79 + "\n")

            # We run pip-compile in ./requirements/ and add only the filenames as arguments
            # So pip-compile add no path to comments ;)

            verbose_check_call(
                "pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in,
                cwd=requirements_path
            )

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
