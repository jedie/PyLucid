# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
from bootstrap.source_prefix_code import AfterInstall


def after_install(options, home_dir):
    # --- CUT here ---
    """
    called after virtualenv was created and setuptools installed.
    Now we installed PyLucid and used libs/packages.
    """
    a = AfterInstall(options, home_dir)
    a.install_packages()
    a.symlink_scripts()

    sys.stdout.write("\n")
    sys.stdout.write("PyLucid environment created in: %s\n" % c.colorize(home_dir, foreground="blue", opts=("bold",)))
    sys.stdout.write("\n")
    sys.stdout.write("Now you can create a new page instance, more info:\n")
    sys.stdout.write("http://www.pylucid.org/permalink/355/create-a-new-page-instance\n")
    sys.stdout.write("\n")