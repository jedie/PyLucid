#-----------------------------------------------------------------------------
# PyLucid bootstrap script START

"""
    PyLucid virtual environment bootstrap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file would be merged into pylucid-boot.py with the
    script create_bootstrap_script.py
"""


LIBS = [
    # Python packages
    "feedparser", # http://pypi.python.org/pypi/FeedParser/
    "Pygments", # http://pygments.org/

    # external Django apps
    "django-reversion", # http://code.google.com/p/django-reversion/
    "django-dbtemplates", # http://code.google.com/p/django-dbtemplates/
    "django-tagging", # http://code.google.com/p/django-tagging/
]

MENU_TXT = """
Please select how the pylucid own projects should be checkout:

(1) Python packages from PyPi (no SVN or git needed, not supported, yet!)
(2) source via SVN only (checkout git repository via github svn gateway)
(3) source via git and clone with readonly **preferred**
(4) clone with git push access (Only for PyLucid collaborators)
(5) abort
"""
DEFAULT_MENU_CHOICE = 3

PIP_INSTALL_DATA = {
    1: [# *** use python packages from PyPi
        "python-creole", "django-dbpreferences", "django-tools",
        "PyLucid",
        "Django"
    ],
    2: [# use SVN
        # SVN Version from django:
        ("-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django"),
        # own sub projects
        ("-e", "svn+http://svn.github.com/jedie/python-creole.git#egg=python-creole"),
        ("-e", "svn+http://svn.github.com/jedie/django-dbpreferences.git#egg=dbpreferences"),
        ("-e", "svn+http://svn.github.com/jedie/django-tools.git#egg=django-tools"),
        ("-e", "svn+http://svn.github.com/jedie/PyLucid.git#egg=pylucid"),
    ],
    3: [# git readonly clone
        # SVN Version from django:
        ("-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django"),
        # own sub projects
        ("-e", "git+git://github.com/jedie/python-creole.git#egg=python-creole"),
        ("-e", "git+git://github.com/jedie/django-dbpreferences.git#egg=dbpreferences"),
        ("-e", "git+git://github.com/jedie/django-tools.git#egg=django-tools"),
        ("-e", "git+git://github.com/jedie/PyLucid.git#egg=pylucid"),
    ],
    4: [ # clone with git push access
        # SVN Version from django:
        ("-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django"),
        # own sub projects
        ("-e", "git+git@github.com:jedie/python-creole.git#egg=python-creole"),
        ("-e", "git+git@github.com:jedie/django-dbpreferences.git#egg=dbpreferences"),
        ("-e", "git+git@github.com:jedie/django-tools.git#egg=django-tools"),
        ("-e", "git+git@github.com:jedie/PyLucid.git#egg=pylucid"),
    ]
}
KEYS_STRING = ",".join([str(i) for i in PIP_INSTALL_DATA.keys()])


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


def get_requirement_choice():
    """
    Display menu and select a number.
    """
    input_msg = "%s [%s] (default: %s) " % (
        c.colorize("Please select:", opts=("bold",)),
        KEYS_STRING, c.colorize(DEFAULT_MENU_CHOICE, opts=("bold",))
    )

    while True:
        print MENU_TXT

        try:
            input = raw_input(input_msg)
        except KeyboardInterrupt:
            sys.exit(-1)

        print
        if input == "":
            return DEFAULT_MENU_CHOICE
        try:
            number = int(input)
        except ValueError:
            print c.colorize("Error:", foreground="red"), "Input is not a number!"
        else:
            if number == 5:
                sys.exit(-1)
            elif number not in PIP_INSTALL_DATA:
                print c.colorize("Error:", foreground="red"), "%r is not a valid choice!" % (
                    c.colorize(number, opts=("bold",))
                )
            else:
                return number


def extend_parser(parser):
    """
    extend optparse options.
    """
    parser.add_option("-t", "--type", type="int",
        dest="pip_type", default=None,
        help="pip install type (%r)" % KEYS_STRING
    )



def adjust_options(options, args):
    """
    Display MENU_TXT
    """
    print c.colorize("PyLucid virtual environment bootstrap", opts=("bold", "underscore"))
    print

    try:
        home_dir = args[0]
    except IndexError:
        return # Error message would be created later

    print "Create PyLucid environment in:", c.colorize(home_dir, foreground="blue", opts=("bold",))
    print

    p = SysPath()

    svn_path = p.find("svn")
    if svn_path:
        print "subversion found in:", c.colorize(svn_path, opts=("bold",))
    else:
        print c.colorize("WARNING:", foreground="red", opts=("underscore",)),
        print "subversion not found in path!"

    git_path = p.find("git")
    if git_path:
        print "git found in:", c.colorize(git_path, opts=("bold",))
    else:
        print c.colorize("WARNING:", foreground="red", opts=("underscore",)),
        print "git not found in path!"


    if options.pip_type == None:
        options.pip_type = get_requirement_choice()

    if options.pip_type not in PIP_INSTALL_DATA:
        print "pip type wrong!"
        sys.exit(101)


class AfterInstall(object):
    def __init__(self, options, home_dir):
        self.options = options
        self.home_dir = home_dir
        self.logfile = os.path.abspath(os.path.join(home_dir, "PyLucid_pip.log"))
        bin_dir = os.path.abspath(os.path.join(home_dir, "bin"))
        self.easy_install = os.path.join(bin_dir, "easy_install")
        self.pip_cmd = os.path.join(bin_dir, "pip")

        self.subprocess_defaults = {
            "cwd": bin_dir,
            "env": {
                "VIRTUAL_ENV": home_dir,
                "PATH": bin_dir + ":" + os.environ["PATH"],
            }
        }

    def run_cmd(self, cmd):
        for part in cmd:
            if part.startswith("/") or part.startswith("-"):
                print c.colorize(part, foreground="blue"),
            else:
                print c.colorize(part, foreground="blue", opts=("bold",)),
        print
        subprocess.call(cmd, **self.subprocess_defaults)
        print

    def run_pip(self, info_text, pip_lines):
        print
        print c.colorize(info_text, foreground="green", opts=("bold", "underscore"))

        for pip_line in pip_lines:
            cmd = [self.pip_cmd, "install", "--verbose", "--log=%s" % self.logfile]
            if isinstance(pip_line, (list, tuple)):
                cmd += list(pip_line)
            else:
                cmd.append(pip_line)
            self.run_cmd(cmd)

    def install_pip(self):
        print
        print c.colorize("install pip", foreground="green", opts=("bold", "underscore"))
        if os.path.isfile(self.pip_cmd):
            print "Skip, pip exist at: %s\n" % c.colorize(self.pip_cmd, opts=("bold",))
        else:
            self.run_cmd([self.easy_install, '--always-copy', 'pip'])

    def install_pylucid(self):
        install_type = self.options.pip_type
        install_data = PIP_INSTALL_DATA[install_type]
        self.run_pip("install PyLucid projects", install_data)

    def install_libs(self):
        self.run_pip("install PyLucid libs", LIBS)

    def copy_scripts(self):
        # copy manage.sh into env root directory
        source_path = os.path.join(self.home_dir, "src", "pylucid", "scripts", "create_page_instance.sh")
        print("\ncopy: %s\nto: %s\n" % (
            c.colorize(source_path, opts=("bold",)),
            c.colorize(self.home_dir, opts=("bold",)))
        )
        shutil.copy2(source_path, self.home_dir)


def after_install(options, home_dir):
    """
    called after virtualenv was created and setuptools installed.
    Now we installed PyLucid and used libs/packages.
    """
    a = AfterInstall(options, home_dir)
    a.install_pip()
    a.install_pylucid()
    a.install_libs()
    a.copy_scripts()


# PyLucid bootstrap script END
#-----------------------------------------------------------------------------
