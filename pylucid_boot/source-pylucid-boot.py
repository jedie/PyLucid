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
---------------------------------------------------------------------
Please select how the pylucid own projects should be checkout:

(1) Python packages from PyPi (no SVN or git needed)
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
        "-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django",
        # own sub projects
        "-e", "svn+http://svn.github.com/jedie/python-creole.git#egg=python-creole",
        "-e", "svn+http://svn.github.com/jedie/django-dbpreferences.git#egg=dbpreferences",
        "-e", "svn+http://svn.github.com/jedie/django-tools.git#egg=django-tools",
        "-e", "svn+http://svn.github.com/jedie/PyLucid.git#egg=pylucid",
    ],
    3: [# git readonly clone
        # SVN Version from django:
        "-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django",
        # own sub projects
        "-e", "git+git://github.com/jedie/python-creole.git#egg=python-creole",
        "-e", "git+git://github.com/jedie/django-dbpreferences.git#egg=dbpreferences",
        "-e", "git+git://github.com/jedie/django-tools.git#egg=django-tools",
        "-e", "git+git://github.com/jedie/PyLucid.git#egg=pylucid",
    ],
    4: [ # clone with git push access
        # SVN Version from django:
        "-e", "svn+http://code.djangoproject.com/svn/django/trunk/#egg=django",
        # own sub projects
        "-e", "git+git@github.com:jedie/python-creole.git#egg=python-creole",
        "-e", "git+git@github.com:jedie/django-dbpreferences.git#egg=dbpreferences",
        "-e", "git+git@github.com:jedie/django-tools.git#egg=django-tools",
        "-e", "git+git@github.com:jedie/PyLucid.git#egg=pylucid",
    ]
}
KEYS_STRING = ",".join([str(i) for i in PIP_INSTALL_DATA.keys()])


def get_requirement_choice():
    """
    Display menu and select a number.
    """
    while True:
        print MENU_TXT

        try:
            input = raw_input(
                "Please select: [%s] (default: %s) " % (KEYS_STRING, DEFAULT_MENU_CHOICE)
            )
        except KeyboardInterrupt:
            sys.exit(-1)

        print
        if input == "":
            return DEFAULT_MENU_CHOICE
        try:
            number = int(input)
        except ValueError:
            print "Error: Input is not a number!"
        else:
            if number == 5:
                sys.exit(-1)
            elif number not in PIP_INSTALL_DATA:
                print "Error: %r is not a valid choise!" % number
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
    You can change options here, or change the args (if you accept
    different kinds of arguments, be sure you modify ``args`` so it is
    only ``[DEST_DIR]``).
    """

    print "\nCreate PyLucid environment in:", args[0]

    if options.pip_type == None:
        options.pip_type = get_requirement_choice()

    if options.pip_type not in PIP_INSTALL_DATA:
        print "pip type wrong!"
        sys.exit(101)


def verbose_copy(src, dst):
    print("\ncopy: %r\nto: %r\n" % (src, dst))
    shutil.copy2(src, dst)


def after_install(options, home_dir):
    """
    called after virtualenv was created and setuptools installed.
    Now we installed PyLucid and used libs/packages.
    """
    bin_dir = os.path.abspath(os.path.join(home_dir, "bin"))

    defaults = {
        "cwd": bin_dir,
        "env": {
            "VIRTUAL_ENV": home_dir,
            "PATH": bin_dir + ":" + os.environ["PATH"],
        }
    }
    easy_install = os.path.join(bin_dir, "easy_install")
    pip = os.path.join(bin_dir, "pip")

    print "-" * 79
    print "install pip"
    if os.path.isfile(pip):
        print "Skip, pip exist at: %s" % pip
    else:
        cmd = [easy_install, '--always-copy', 'pip']
        print " ".join(cmd)
        subprocess.call(cmd, **defaults)


    PIP_LOG = os.path.abspath(os.path.join(home_dir, "PyLucid_pip.log"))

    pip_type = options.pip_type
    pip_names = PIP_INSTALL_DATA[pip_type]

    print "-" * 79
    print "install PyLucid projects"
    cmd = [pip, "install", "--verbose", "--log=%s" % PIP_LOG] + pip_names
    print " ".join(cmd)
    subprocess.call(cmd, **defaults)

    print "-" * 79
    print "install PyLucid libs"
    cmd = [pip, "install", "--verbose", "--log=%s" % PIP_LOG] + LIBS
    print " ".join(cmd)
    subprocess.call(cmd, **defaults)

    # copy manage.sh into env root directory
    source_path = os.path.join(home_dir, "src", "pylucid", "scripts", "create_page_instance.sh")
    verbose_copy(source_path, home_dir)


# PyLucid bootstrap script END
#-----------------------------------------------------------------------------
