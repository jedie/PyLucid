#-----------------------------------------------------------------------------
# PyLucid bootstrap script START

"""
    PyLucid virtual environment bootstrap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file would be merged into pylucid-boot.py with the
    script create_bootstrap_script.py
"""


MENU_TXT = """
Please select how the pylucid own projects should be checkout:

(1) normal installation
(2) developer installation
"""
INSTALL_NORMAL = "normal"
INSTALL_DEV = "developer"
CHOICES = {"1":INSTALL_NORMAL, "2":INSTALL_DEV}
DEFAULT_MENU_CHOICE = CHOICES["1"]


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
    choice_keys = CHOICES.keys()
    input_msg = "%s (%s) (default: %s) " % (
        c.colorize("Please select:", opts=("bold",)),
        "/".join(choice_keys),
        DEFAULT_MENU_CHOICE
    )

    print MENU_TXT
    try:
        input = raw_input(input_msg)
    except KeyboardInterrupt:
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    if input == "":
        return DEFAULT_MENU_CHOICE

    try:
        return CHOICES[input]
    except KeyError:
        print c.colorize("Error:", foreground="red"), "%r is not a valid choice!" % (
            c.colorize(number, opts=("bold",))
        )
        sys.exit(-1)


def extend_parser(parser):
    """
    extend optparse options.
    """
    parser.add_option("-t", "--type", type="string",
        dest="pip_type", default=None,
        help="pip install type: %s" % ", ".join(CHOICES.values())
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

    git_path = p.find("git")
    if git_path:
        print "git found in:", c.colorize(git_path, opts=("bold",))
    else:
        print c.colorize("ERROR:", foreground="red", opts=("underscore",)),
        print "git not found in path!"

    if options.pip_type == None:
        options.pip_type = get_requirement_choice()
    elif options.pip_type not in CHOICES.values():
        print "pip type wrong!"
        sys.exit(-1)


class AfterInstall(object):
    def __init__(self, options, home_dir):
        self.options = options
        self.home_dir = home_dir
        self.abs_home_dir = os.path.abspath(home_dir)
        self.logfile = os.path.join(self.abs_home_dir, "PyLucid_pip.log")
        bin_dir = os.path.join(self.abs_home_dir, "bin")
        self.easy_install = os.path.join(bin_dir, "easy_install")
        self.pip_cmd = os.path.join(bin_dir, "pip")

        self.subprocess_defaults = {
            "cwd": bin_dir,
            "env": {
                "VIRTUAL_ENV": home_dir,
                "PATH": bin_dir + ":" + os.environ["PATH"],
            }
        }

        # NORMAL_INSTALLATION and DEVELOPER_INSTALLATION added by create_bootstrap_script.py!
        if self.options.pip_type == INSTALL_NORMAL:
            self.dev_install = False
        elif self.options.pip_type == INSTALL_DEV:
            self.dev_install = True
        else:
            raise ValueError

    def run_cmd(self, cmd):
        print "_" * 79
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
            cmd = [self.pip_cmd, "install", "--log=%s" % self.logfile]
            if isinstance(pip_line, (list, tuple)):
                cmd += list(pip_line)
            else:
                cmd.append(pip_line)
            self.run_cmd(cmd)

    def install_pip(self):
        print
        if os.path.isfile(self.pip_cmd):
            print c.colorize("update existing pip", foreground="green", opts=("bold", "underscore"))
            self.run_cmd([self.pip_cmd, 'install', "--upgrade", 'pip'])
        else:
            print c.colorize("install pip", foreground="green", opts=("bold", "underscore"))
            self.run_cmd([self.easy_install, '--always-copy', 'pip'])

    def install_packages(self):
        if self.dev_install:
            install_data = DEVELOPER_INSTALLATION
        else:
            install_data = NORMAL_INSTALLATION

        self.run_pip("install PyLucid projects", install_data)

    def verbose_symlink(self, source_path, dst_path):
        print("\nsymlink: %s\nto: %s\n" % (
            c.colorize(source_path, opts=("bold",)),
            c.colorize(dst_path, opts=("bold",)))
        )
        try:
            os.symlink(source_path, dst_path)
        except Exception, e:
            import traceback
            sys.stderr.write(traceback.format_exc())

    def symlink_scripts(self):
        """ symlink needfull scripts into env root directory """
        def symlink_pylucid_script(filename):
            source_path = os.path.join(self.abs_home_dir, "src", "pylucid", "scripts", filename)
            dst_path = os.path.join(self.abs_home_dir, filename)
            self.verbose_symlink(source_path, dst_path)

        # symlink some PyLucid scripts from pylucid/scripts/ into virtualenv root
        symlink_pylucid_script("create_page_instance.sh")

        if self.dev_install:
            symlink_pylucid_script("upgrade_pylucid_dev_env.sh")
        else:
            symlink_pylucid_script("upgrade_pylucid_env.sh")

#        # symlink "upgrade_virtualenv.py" from django-tools into  virtualenv root
#        filename = "upgrade_virtualenv.py"
#        source_path = os.path.join(self.abs_home_dir, "src", "django-tools", "django_tools", filename)
#        dst_path = os.path.join(self.abs_home_dir, filename)
#        self.verbose_symlink(source_path, dst_path)



def after_install(options, home_dir):
    """
    called after virtualenv was created and setuptools installed.
    Now we installed PyLucid and used libs/packages.
    """
    a = AfterInstall(options, home_dir)
    a.install_pip()
    a.install_packages()
    a.symlink_scripts()

    print
    print "PyLucid environment created in:", c.colorize(home_dir, foreground="blue", opts=("bold",))
    print
    print "Now you can create a new page instance, more info:"
    print "http://www.pylucid.org/permalink/355/create-a-new-page-instance"
    print

# PyLucid bootstrap script END
#-----------------------------------------------------------------------------
