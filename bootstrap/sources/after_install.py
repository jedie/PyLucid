# coding: utf-8

"""
    PyLucid bootstrap
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2014-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# imports not really needed and just for the editor warning ;)
import sys
from bootstrap.sources.prefix_code import AfterInstall, c


def after_install(options, home_dir):
    # --- CUT here ---
    """
    called after virtualenv was created and setuptools installed.
    Now we installed PyLucid and used libs/packages.
    """
    a = AfterInstall(options, home_dir)
    a.install_packages()

    sys.stdout.write("\n")
    sys.stdout.write("PyLucid environment created in: %s\n" % c.colorize(home_dir, foreground="blue", opts=("bold",)))
    sys.stdout.write("\n")

    sys.stdout.write("Now you can create a new page instance with %s\n" % c.colorize("pylucid_install", foreground="blue", opts=("bold",)))
    sys.stdout.write("\n")

    sys.stdout.write("More Info:\n")
    sys.stdout.write("https://github.com/jedie/PyLucid#create-page-instance\n")
    sys.stdout.write("\n")