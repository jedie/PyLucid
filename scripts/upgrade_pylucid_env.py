#!/usr/bin/env python
# coding: utf-8

import os
import sys
import subprocess
from optparse import OptionParser

if __name__ == "__main__":
    # precheck if we in a activated virtualenv
    # if not, the pip import can raise a ImportError, if pip not installed
    # in the globale python environment
    if not hasattr(sys, 'real_prefix'):
        print("")
        print("Error: It seems that we are not running in a activated virtualenv!")
        print("")
        print("Please activate your environment first, e.g:")
        print("\t...my_env$ source bin/activate")
        print("")
        sys.exit(-1)

import pkg_resources

from pip import locations
from pip.util import get_terminal_size
import pip

try:
    import pylucid_project
except ImportError, err:
    print "Import error:", err
    print
    print "Not running in activated virtualenv?"
    print
    sys.exit(-1)

PYLUCID_BASE_PATH = os.path.abspath(os.path.dirname(pylucid_project.__file__))

def get_req_path(filename):
    filepath = os.path.join(PYLUCID_BASE_PATH, "../requirements", filename)
    if not os.path.exists(filepath):
        print "ERROR: file %r doesn't exists!" % filepath
        sys.exit(-1)
    return filepath


INSTALL_NORMAL = "normal"
INSTALL_DEV = "developer"
CHOICES = {
    INSTALL_NORMAL:"normal_installation.txt",
    INSTALL_DEV:"developer_installation.txt",
}




class ColorOut(object):
    """
    Borrowed from Django:
    http://code.djangoproject.com/browser/django/trunk/django/utils/termcolors.py
    
    >>> c = ColorOut()
    >>> c.supports_colors()
    True
    >>> c.color_support = True
    >>> c.colorize('no color')
    'no color'
    >>> c.colorize('bold', opts=("bold",))
    '\\x1b[1mbold\\x1b[0m'
    >>> c.colorize("colors!", foreground="red", background="blue", opts=("bold", "blink"))
    '\\x1b[31;44;1;5mcolors!\\x1b[0m'
    """
    color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
    foreground_colors = dict([(color_names[x], '3%s' % x) for x in range(8)])
    background_colors = dict([(color_names[x], '4%s' % x) for x in range(8)])
    opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

    def __init__(self):
        self.color_support = self.supports_colors()

    def supports_colors(self):
        if sys.platform in ('win32', 'Pocket PC'):
            return False

        # isatty is not always implemented!
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        else:
            return False

    def colorize(self, text, foreground=None, background=None, opts=()):
        """
        Returns your text, enclosed in ANSI graphics codes.
        """
        if not self.color_support:
            return text

        code_list = []

        if foreground:
            code_list.append(self.foreground_colors[foreground])
        if background:
            code_list.append(self.background_colors[background])

        for option in opts:
            code_list.append(self.opt_dict[option])

        if not code_list:
            return text

        return "\x1b[%sm%s\x1b[0m" % (';'.join(code_list), text)
c = ColorOut()


def check_activation():
    print("")
    print("sys.real_prefix: %s" % c.colorize(sys.real_prefix, foreground="magenta"))
    print("sys.prefix: %s" % c.colorize(sys.prefix, foreground="green", opts=("bold",)))
    print("use pip from: %s" % c.colorize(os.path.dirname(pip.__file__), foreground="blue", opts=("bold",)))
    print("")


def check_pip_version():
    try:
        pkg_resources.require("pip >= 1.0.1")
    except pkg_resources.VersionConflict, err:
        print(c.colorize("Error: outdated pip version!", foreground="red"))
        print("Original error: %s" % err)
        print("")
        print("You should upgrade pip, e.g.:")
        print("\tpip install --upgrade pip")
        print("")


def print_options(options):
    output = []
    if options.dryrun:
        output.append("dry-run is on")
    if options.verbose:
        output.append("pip verbose mode is on")
    output.append("log saved in '%s'" % options.logfile)

    print(c.colorize("used options:", opts=("underscore",)))
    for line in output:
        print(c.colorize("\t* %s" % line, foreground="magenta"))


def parse_requirements(filename):
    filepath = get_req_path(filename)
    f = file(filepath, "r")
    entries = []
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r"):
            recursive_filename = line.split("-r ")[1]
            entries += parse_requirements(recursive_filename)
            continue
        if line.startswith("-e"):
            url = line.split("-e ")[1]
            entries.append("--editable=%s" % url)
        else:
            entries.append(line)
    f.close()
    return entries


def call_pip(options, *args):
    pip_executeable = os.path.join(locations.bin_py, "pip")
    cmd = [
        pip_executeable, "install", "--upgrade", "--no-dependencies",
        "--download-cache=%s" % options.download_cache
    ]
    if options.verbose:
        cmd.append("--verbose")
    if options.logfile:
        cmd.append("--log=%s" % options.logfile)
    cmd += args
    print("_" * get_terminal_size()[0])
    print(c.colorize(" ".join(cmd), foreground="blue"))
    if not options.dryrun:
        subprocess.call(cmd)


def select_requirement(options, filename):
    requirements = parse_requirements(filename)

    print "\nWhich package should be upgraded?\n"
    for no, requirement in enumerate(requirements):
        print "(%i) %s" % (no, requirement)

    print "(a) upgrade all packages"

    try:
        input = raw_input("\nPlease select (one entry or comma seperated):")
    except KeyboardInterrupt:
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    selection = [i for i in input.split(",") if i.strip()]
    if len(selection) == 0:
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    print "Your selection:", repr(selection)

    if "a" in selection:
        print "Upgrade all packages."
        return requirements

    req_dict = dict([(str(no), r) for no, r in enumerate(requirements)])
    selected_req = []
    for item in selection:
        print "%s\t" % item,
        try:
            req = req_dict[item]
        except KeyError:
            print "(Invalid, skip.)"
        else:
            print req
            selected_req.append(req)

    return selected_req


def do_upgrade(options, requirements):
    for requirement in requirements:
        call_pip(options, requirement)


def main():
    parser = OptionParser()
    parser.add_option("-t", "--env_type", type="string",
        dest="env_type", default=None,
        help="PyLucid env install type: %s" % ", ".join(CHOICES.keys())
    )
    parser.add_option("--dry-run",
                      action="store_true", dest="dryrun", default=False,
                      help="display only the pip commands and do nothing.")
    parser.add_option("--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Turn on pip verbose mode")
    parser.add_option("--log",
                      action="store", dest="logfile", default="upgrade_pylucid_env.log",
                      help="Log file where complete pip output will be kept")
    parser.add_option("--download-cache",
                      action="store", dest="download_cache",
                      default=os.path.join(sys.prefix, "pypi_cache"),
                      help="Cache downloaded packages in DIR")


    options, args = parser.parse_args()
#    print options, args

    if not options.env_type:
        print(c.colorize("\nError: No env type given!\n", foreground="red", opts=("bold",)))
        parser.print_help()
        sys.exit(-1)

    try:
        filename = CHOICES[options.env_type]
    except KeyError:
        print(c.colorize("\nError: Wrong env type!\n", foreground="red", opts=("bold",)))
        parser.print_help()
        sys.exit(-1)

    check_activation()
    check_pip_version()

    print_options(options)

    requirements = select_requirement(options, filename)
    if len(requirements) == 0:
        print "Nothing to upgrade, abort."
        sys.exit()

    try:
        input = raw_input("\nStart upgrade (y/n) ?")
    except KeyboardInterrupt:
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()
    if input.lower() not in ("y", "j"):
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    do_upgrade(options, requirements)

    print("-"*get_terminal_size()[0])

    print("")
    print(c.colorize("PyLucid virtual environment updated.", foreground="blue"))
    if options.dryrun:
        print("dry-run: nothing changes.")
    else:
        print("Look into %s for more information." % options.logfile)
    print("")


if __name__ == "__main__":
    main()


