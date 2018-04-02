#!/usr/bin/python3

"""
    PyLucid Admin Shell
    ~~~~~~~~~~~~~~~~~~~

    :created: 2018 by Jens Diemer
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
from pathlib import Path

# Bootstrap-Env
import pylucid
from pylucid.admin_shell.normal_shell import PyLucidNormalShell
from pylucid.admin_shell.requirements import Requirements

log = logging.getLogger(__name__)

SELF_FILE_PATH=Path(pylucid.__file__).resolve()                 # .../src/pylucid/pylucid/__init__.py
PACKAGE_PATH=Path(SELF_FILE_PATH.parent).resolve()                 # .../src/pylucid/pylucid/
BOOT_FILE_PATH=Path(PACKAGE_PATH, "pylucid_boot.py").resolve()     # .../src/pylucid/pylucid/pylucid_boot.py
OWN_FILE_NAME=Path(__file__).name                               # pylucid_admin.py

assert SELF_FILE_PATH.is_file()
assert PACKAGE_PATH.is_dir()
assert BOOT_FILE_PATH.is_file()

# print("SELF_FILE_PATH: %s" % SELF_FILE_PATH)
# print("BOOT_FILE_PATH: %s" % BOOT_FILE_PATH)
# print("PACKAGE_PATH: %s" % PACKAGE_PATH)
# print("OWN_FILE_NAME: %s" % OWN_FILE_NAME)


TEST_REQ_FILE_NAME="test_requirements.txt"



def main():
    assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"

    requirements = Requirements(package_path=PACKAGE_PATH)

    if requirements.normal_mode:
        # Installed in "normal" mode (as Package from PyPi)
        ShellClass = PyLucidNormalShell
    else:
        # Installed in "developer" mode (as editable from source)
        # Import here, because developer_shell imports packages that
        # only installed in "developer" mode ;)
        from pylucid.admin_shell.developer_shell import PyLucidDeveloperShell
        ShellClass = PyLucidDeveloperShell

    ShellClass(
        requirements=requirements,
        self_filename=OWN_FILE_NAME,
        package_path = PACKAGE_PATH,
    ).cmdloop()


if __name__ == '__main__':
    main()
