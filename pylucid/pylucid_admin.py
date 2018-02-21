
import os  # isort:skip

# pylucid.pylucid_boot.in_virtualenv
assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip


import glob
import logging
import re
import subprocess
import sys
from pathlib import Path

import pytest

# PyLucid
from pylucid.pylucid_boot import Cmd2, in_virtualenv, verbose_check_call

log = logging.getLogger(__name__)


__version__ = "0.0.1"


OWN_FILENAME=os.path.basename(__file__)              # .../src/pylucid/pylucid/pylucid_admin.py
SELF_FILEPATH=Path(__file__).resolve()               # .../src/pylucid/pylucid/
BOOT_FILEPATH=Path(SELF_FILEPATH, "pylucid_boot.py") # .../src/pylucid/pylucid/pylucid_boot.py
ROOT_PATH=Path(SELF_FILEPATH, "..", "..").resolve()  # .../src/pylucid/


# Helper to replace the content:
INSERT_START_RE=re.compile(r'(?P<variable>.*?)=""" # insert \[(?P<filename>.*?)\]')
INSERT_END = '"""'


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


class Requirement:
    """
    Helper class to insert requirements/*_installation.txt file content.
    """
    def parse_req_file(self, req_file):
        """
        returns the lines of a requirements/*_installation.txt file.
        Skip comments and emptry lines
        """
        lines = []

        req_file = Path(ROOT_PATH, req_file).resolve()

        print("read %s..." % req_file)
        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                assert not line.startswith("-r"), "'-r' not supported! Not the pip-compile output file?!?"
                lines.append("%s\n" % line)

        return lines

    def update(self):
        new_content = []
        with open(BOOT_FILEPATH, "r") as f:
            in_insert_block=False
            for line in f:
                if not in_insert_block:
                    new_content.append(line)

                if in_insert_block:
                    if line.strip() == INSERT_END:
                        in_insert_block=False
                        new_content.append(line)

                else:
                    m = INSERT_START_RE.match(line)
                    if m:
                        in_insert_block=True
                        m = m.groupdict()
                        variable = m["variable"]
                        filename = m["filename"]
                        print("Fill %r from %r..." % (variable, filename))
                        new_content += self.parse_req_file(filename)


        bak_filename=Path("%s.bak" % BOOT_FILEPATH)
        if bak_filename.is_file():
            print("Remove old backup file: %s" % bak_filename)
            bak_filename.unlink()

        print("Create backup file: %r" % bak_filename)
        BOOT_FILEPATH.rename(bak_filename)

        with open(BOOT_FILEPATH, "w") as f:
            f.writelines(new_content)

        BOOT_FILEPATH.chmod(0o775)


class PyLucidShell(Cmd2):
    own_filename = OWN_FILENAME

    def do_pytest(self, arg):
        """
        Run tests via pytest
        """
        pytest.main()

    def do_pip_freeze(self, arg):
        "run 'pip freeze': FOO"
        verbose_check_call("pip3", "freeze")

    def do_update_env(self, arg):
        """
        Update all packages in virtualenv.

        (Call this command only in a activated virtualenv.)
        """
        if not in_virtualenv():
            self.stdout.write("\nERROR: Only allowed in activated virtualenv!\n\n")
            return

        verbose_check_call("pip3", "install", "--upgrade", "pip")

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

    def do_insert_requirement(self, arg):
        """
        insert requirements/*_installation.txt files into pylucid/pylucid_admin.py
        This will be automaticly done by 'upgrade_requirements'!

        Direct start with:
            $ pylucid_admin insert_requirement
        """
        Requirement().update()

    def do_upgrade_requirements(self, arg):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.
        3. insert requirement content into pylucid_admin.py

        Direct start with:
            $ pylucid_admin upgrade_requirements
        """

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

        self.do_insert_requirement(arg)


def main():
    PyLucidShell().cmdloop()


if __name__ == '__main__':
    main()
