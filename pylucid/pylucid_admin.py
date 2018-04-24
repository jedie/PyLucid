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

from bootstrap_env.admin_shell.path_helper import PathHelper

# PyLucid
import pylucid
from pylucid.admin_shell.normal_shell import PyLucidNormalShell
from pylucid.admin_shell.path_helper import get_path_helper_instance

log = logging.getLogger(__name__)


TEST_REQ_FILE_NAME="test_requirements.txt"


def main():
    assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"

    path_helper = get_path_helper_instance()
    # path_helper.print_path()
    # path_helper.assert_all_path()

    if path_helper.normal_mode:
        # Installed in "normal" mode (as Package from PyPi)
        ShellClass = PyLucidNormalShell
    else:
        # Installed in "developer" mode (as editable from source)
        # Import here, because developer_shell imports packages that
        # only installed in "developer" mode ;)
        from pylucid.admin_shell.developer_shell import PyLucidDeveloperShell
        ShellClass = PyLucidDeveloperShell

    ShellClass(
        path_helper,
        self_filename=Path(__file__).name
    ).cmdloop()


if __name__ == '__main__':
    main()
