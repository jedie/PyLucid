# coding: utf-8

"""
    PyLucid bootstrap
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2014-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# imports not really needed and just for the editor warning ;)
import os
import sys
import subprocess


# Will be inserted in real bootstrap file ;)
DEVELOPER_INSTALLATION=None
NORMAL_INSTALLATION=None


# --- CUT here ---


MENU_TXT = """
Please select how the pylucid own projects should be checkout:

(1) normal PyPi installation    !!!Currently not supported!!!
(2) git installation (readonly) <<--use this!
(3) developer installation      !!!github write access needed!!!

"""

INSTALL_NORMAL = "normal"
INSTALL_READONLY = "readonly"
INSTALL_DEV = "developer"
CHOICES = {"1":INSTALL_NORMAL, "2":INSTALL_READONLY, "3":INSTALL_DEV}
DEFAULT_MENU_CHOICE_NO = "2"
DEFAULT_MENU_CHOICE = CHOICES[DEFAULT_MENU_CHOICE_NO]


PY2 = sys.version_info[0] == 2
if PY2:
    # input=raw_input
    raise NotImplementedError("Python 3 is currently not Supported! Please use Python 3 !!!")


class SysPath(object):
    """
    Helper to find a file in system path.
    >>> SysPath().find("python")
    '/usr/bin/python'
    """
    def __init__(self):
        self.sys_path = os.environ["PATH"].split(":")

    def find(self, filename):
        for path in self.sys_path:
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                return filepath


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
    def __init__(self):
        color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')

        self.foreground_colors = dict([(color_names[x], '3%s' % x) for x in range(8)])
        self.background_colors = dict([(color_names[x], '4%s' % x) for x in range(8)])
        self.opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

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


def get_requirement_choice():
    """
    Display menu and select a number.
    """
    choice_keys = list(CHOICES.keys())
    input_msg = "%s (%s) (default: %s) " % (
        c.colorize("Please select:", opts=("bold",)),
        "/".join(choice_keys),
        DEFAULT_MENU_CHOICE_NO
    )

    sys.stderr.write(MENU_TXT)
    try:
        inkey = input(input_msg)
    except KeyboardInterrupt:
        sys.stderr.write(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    if inkey == "":
        return DEFAULT_MENU_CHOICE

    try:
        return CHOICES[inkey]
    except KeyError:
        sys.stderr.write(c.colorize("Error:", foreground="red"))
        sys.stderr.write("%s is not a valid choice!\n" % c.colorize(inkey, opts=("bold",)))
        sys.exit(-1)


class AfterInstall(object):
    def __init__(self, options, home_dir):
        self.options = options
        self.home_dir = home_dir
        self.abs_home_dir = os.path.abspath(home_dir)
        self.logfile = os.path.join(self.abs_home_dir, "PyLucid_pip.log")
        bin_dir = os.path.join(self.abs_home_dir, "bin")
        self.python_cmd = os.path.join(bin_dir, "python")
        self.pip_cmd = os.path.join(bin_dir, "pip")

        self.subprocess_defaults = {
            "cwd": bin_dir,
            "env": {
                "VIRTUAL_ENV": home_dir,
                "PATH": bin_dir + ":" + os.environ["PATH"],
            }
        }

    def run_cmd(self, cmd):
        sys.stderr.write("\n")
        sys.stderr.write("_" * 79)
        sys.stderr.write("\n")
        for part in cmd:
            if part.startswith("/") or part.startswith("-"):
                sys.stderr.write(c.colorize(part, foreground="blue"))
                sys.stderr.write(" ")
            else:
                sys.stderr.write(c.colorize(part, foreground="blue", opts=("bold",)))
                sys.stderr.write(" ")
        sys.stderr.write("\n")
        subprocess.call(cmd, **self.subprocess_defaults)
        sys.stderr.write("\n")

    def run_pip(self, info_text, pip_lines):
        sys.stderr.write("\n")
        sys.stderr.write(c.colorize(info_text, foreground="green", opts=("bold", "underscore")))
        sys.stderr.write("\n")

        for pip_line in pip_lines:
            assert isinstance(pip_line, str)
            cmd = [self.pip_cmd, "install", "--log=%s" % self.logfile, pip_line]

            if "PyLucid.git" in pip_line or "django-processinfo" in pip_line:
                # FIXME: How to handle this better?
                #
                # PyLucid setup.py does contains all dependencies and it will
                # fail on django-compressor==dev with python 2.6, see:
                #     https://github.com/jedie/PyLucid/issues/74
                #
                # django-processinfo has "Django>=1.3,<1.5" which is
                # Django v1.3.x - v1.4.x and will install django 1.3
                #
                cmd.append("--no-dependencies")

            self.run_cmd(cmd)

    def install_packages(self):
        """
        DEVELOPER_INSTALLATION and NORMAL_INSTALLATION would be inserted
        via create_bootstrap_script.py
        """
        assert self.options.install_type in (INSTALL_NORMAL, INSTALL_READONLY, INSTALL_DEV)

        if self.options.install_type == INSTALL_NORMAL:
            install_data = NORMAL_INSTALLATION
        else:
            install_data = DEVELOPER_INSTALLATION
            if self.options.install_type == INSTALL_READONLY:
                install_data = [
                    entry.replace("git+git@github.com:", "git+https://github.com/")
                    for entry in install_data
                ]

        self.run_pip("install PyLucid projects", install_data)

    def verbose_symlink(self, source_path, dst_path):
        sys.stderr.write("\n")
        sys.stderr.write("symlink: %s\n" % c.colorize(source_path, opts=("bold",)))
        sys.stderr.write("to: %s\n" % c.colorize(dst_path, opts=("bold",)))

        try:
            os.symlink(source_path, dst_path)
        except Exception as e:
            import traceback
            sys.stderr.write(traceback.format_exc())