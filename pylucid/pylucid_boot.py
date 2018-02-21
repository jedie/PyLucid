#!/usr/bin/python3

"""
    PyLucid Boot Admin
    ~~~~~~~~~~~~~~~~~~

    A interactive shell for booting PyLucid.

    Note:
        - This file is "self contained".
        - It used **only** stuff from Python lib.
        - So it's "run able" on a bare python 3 installation
        - On debian / ubuntu the 'python3-venv' package is needed!

    usage, e.g.:

        $ wget https://raw.githubusercontent.com/jedie/PyLucid/pylucid_v3/pylucid/pylucid_boot.py
        $ python3 pylucid_boot.py

        pylucid_boot.py> boot ~/PyLucid_env

    :created: 08.02.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

import cmd
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path

try:
    import venv
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'venv' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)

try:
    import ensurepip
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'ensurepip' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)


__version__ = "0.0.1"


if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)


log = logging.getLogger(__name__)


OWN_FILENAME=os.path.basename(__file__) # .../src/pylucid/pylucid/pylucid_boot.py


#
# The following Variables CI_INSTALL_TXT, DEVELOPER_INSTALL_TXT and NORMAL_INSTALL_TXT are filled
# automatically from the requirements files by:
#   pylucid.pylucid_admin.PyLucidShell.do_upgrade_requirements()
#
# e.g.:
#
# $ pylucid_admin upgrade_requirements
#


CI_INSTALL_TXT=""" # insert [requirements/ci_installation.txt]
-e git+https://github.com/jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+https://github.com/jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+https://github.com/jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+https://github.com/jedie/PyLucid.git@develop#egg=pylucid
aldryn-apphooks-config==0.3.3  # via djangocms-blog
certifi==2018.1.18        # via requests
chardet==3.0.4            # via requests
cmsplugin-filer==1.1.3
cmsplugin-pygments==0.8.2
coverage==4.5.1           # via coveralls
coveralls==1.2.0
django-appconf==1.0.2     # via cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai
django-cms-tools==0.6.0
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar-django-info==0.3.0
django-debug-toolbar==1.9.1
django-filer==1.3.0
django-formtools==2.1     # via django-cms
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.3   # via django-filer
django-reversion-compare==0.6.3
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via djangocms-blog
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-tools==0.38.9
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.9.0
djangocms-htmlsitemap==0.2.0
docopt==0.6.2             # via coveralls
docutils==0.14
easy-thumbnails==2.4.2    # via cmsplugin-filer, django-filer, djangocms-blog
html5lib==1.0.1           # via textile
idna==2.6                 # via requests
lxml==4.1.1               # via django-tools
markdown==2.6.11
pillow==5.0.0
pygments==2.1.3
python-creole==1.3.1
pytz==2018.3              # via djangocms-blog
rcssmin==1.0.6            # via django-compressor
requests==2.18.4          # via coveralls
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via html5lib, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
unidecode==0.4.21         # via django-filer
urllib3==1.22             # via requests
webencodings==0.5.1       # via html5lib
"""


DEVELOPER_INSTALL_TXT=""" # insert [requirements/developer_installation.txt]
-e git+git@github.com:jedie/bootstrap_env.git#egg=bootstrap_env
-e git+git@github.com:jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+git@github.com:jedie/cmsplugin-pygments.git#egg=cmsplugin-pygments
-e git+git@github.com:jedie/django-cms-tools.git@master#egg=django-cms-tools
-e git+git@github.com:jedie/django-debug-toolbar-django-info.git#egg=django-debug-toolbar-django-info
-e git+git@github.com:jedie/django-reversion-compare.git@stable/v0.6.x#egg=django-reversion-compare
-e git+git@github.com:jedie/django-tools.git@master#egg=django-tools
-e git+git@github.com:jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+git@github.com:jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+git@github.com:jedie/PyLucid.git@develop#egg=pylucid
-e git+git@github.com:jedie/python-creole.git#egg=python-creole
aldryn-apphooks-config==0.3.3  # via djangocms-blog
certifi==2018.1.18        # via requests
chardet==3.0.4            # via requests
click==6.7                # via pip-tools
cmsplugin-filer==1.1.3
django-appconf==1.0.2     # via cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar==1.9.1
django-extensions==1.9.9
django-filer==1.3.0
django-formtools==2.1     # via django-cms
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.3   # via django-filer
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via djangocms-blog
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.9.0
djangocms-htmlsitemap==0.2.0
docutils==0.14
easy-thumbnails==2.4.2    # via cmsplugin-filer, django-filer, djangocms-blog
first==2.0.1              # via pip-tools
html5lib==1.0.1           # via textile
idna==2.6                 # via requests
lxml==4.1.1
markdown==2.6.11
pillow==5.0.0
pip-tools==1.11.0
piprot==0.9.7
pkginfo==1.4.1            # via twine
pygments==2.1.3
pytz==2018.3              # via djangocms-blog
rcssmin==1.0.6            # via django-compressor
requests-futures==0.9.7   # via piprot
requests-toolbelt==0.8.0  # via twine
requests==2.18.4          # via piprot, requests-futures, requests-toolbelt, twine
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via django-extensions, html5lib, pip-tools, piprot, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
tqdm==4.19.5              # via twine
twine==1.9.1
typing==3.6.4             # via django-extensions
unidecode==0.4.21         # via django-filer
urllib3==1.22             # via requests
virtualenv==15.1.0
webencodings==0.5.1       # via html5lib
werkzeug==0.14.1
wheel==0.30.0
"""


NORMAL_INSTALL_TXT=""" # insert [requirements/normal_installation.txt]
-e git+https://github.com/jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+https://github.com/jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+https://github.com/jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+https://github.com/jedie/PyLucid.git@develop#egg=pylucid
aldryn-apphooks-config==0.3.3  # via djangocms-blog
cmsplugin-filer==1.1.3
cmsplugin-pygments==0.8.2
django-appconf==1.0.2     # via cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai
django-cms-tools==0.6.0
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar-django-info==0.3.0
django-debug-toolbar==1.9.1
django-filer==1.3.0
django-formtools==2.1     # via django-cms
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.3   # via django-filer
django-reversion-compare==0.6.3
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via djangocms-blog
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-tools==0.38.9
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.9.0
djangocms-htmlsitemap==0.2.0
docutils==0.14
easy-thumbnails==2.4.2    # via cmsplugin-filer, django-filer, djangocms-blog
html5lib==1.0.1           # via textile
lxml==4.1.1               # via django-tools
markdown==2.6.11
pillow==5.0.0
pygments==2.1.3
python-creole==1.3.1
pytz==2018.3              # via djangocms-blog
rcssmin==1.0.6            # via django-compressor
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via html5lib, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
unidecode==0.4.21         # via django-filer
webencodings==0.5.1       # via html5lib
"""


def in_virtualenv():
    # Maybe this is not the best way?!?
    return "VIRTUAL_ENV" in os.environ


if in_virtualenv():
    print("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))
else:
    print("We are not in a virtualenv, ok.")


def verbose_check_call(*popenargs, **kwargs):
    """
    'verbose' version of subprocess.check_output()
    """
    print("Call: %r" % " ".join(popenargs))
    try:
        subprocess.check_call(popenargs, universal_newlines=True, stderr=subprocess.STDOUT, **kwargs)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise
    print("")


def display_errors(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            return "%s: %s" % (err.__class__.__name__, err)

    return wrapped


class Cmd2(cmd.Cmd):
    """
    Enhanced version of 'Cmd' class:
        - command alias
        - methods can be called directly from commandline: e.g.: ./foobar.py --help
        - Display
    """
    own_filename = OWN_FILENAME

    command_alias = { # used in self.precmd()
        "q": "quit", "EOF": "quit",
        "--help": "help", "-h": "help", "-?": "help",
    }

    # Will be append to 'doc_leader' in self.do_help():
    complete_hint="\nUse <{key}> to command completion.\n"
    missing_complete="\n(Sorry, no command completion available.)\n" # if 'readline' not available

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.intro = (
            '\n{filename} shell v{version}\n'
            'Type help or ? to list commands.\n'
        ).format(
            filename=self.own_filename,
            version=__version__
        )

        self.prompt = '%s> ' % self.own_filename

        self.doc_leader = (
            "\nHint: All commands can be called directly from commandline.\n"
            "e.g.: $ ./{filename} pip_freeze\n"
        ).format(
            filename=self.own_filename,
        )

        # e.g.: $ pylucid_admin.py boot /tmp/PyLucid-env -> run self.do_boot("/tmp/PyLucid-env") on startup
        args = sys.argv[1:]
        if args:
            self.cmdqueue = [" ".join(args)]

    @display_errors
    def _complete_path(self, text, line, begidx, endidx):
        """
        complete a command argument with a existing path

        usage e.g.:
            class FooCmd(Cmd2):
                def complete_foobar(self, text, line, begidx, endidx):
                    return self._complete_path(text, line, begidx, endidx)

                def do_foobar(self, path): # 'path' is type string!
                    print("path:", path)
        """
        try:
            destination = line.split(" ", 1)[1]
        except IndexError:
            destination = "."

        if destination=="~":
            return [os.sep]

        destination = Path(destination).expanduser().resolve()

        if not destination.is_dir():
            destination = destination.parent.resolve()

        if destination.is_dir():
            complete_list = [x.stem + os.sep for x in destination.iterdir() if x.is_dir()]
            if text:
                if text in complete_list:
                    return [text + os.sep]

                complete_list = [x for x in complete_list if x.startswith(text)]
        else:
            complete_list = []

        return complete_list

    _complete_hint_added=False
    def do_help(self, arg):
        """
        List available commands with "help" or detailed help with "help cmd".
        """
        if not self._complete_hint_added:
            try:
                import readline
            except ImportError:
                self.doc_leader += self.missing_complete
            else:
                self.doc_leader += self.complete_hint.format(key=self.completekey)
            self._complete_hint_added=True

        return super().do_help(arg)

    def do_quit(self, arg):
        "Exit this interactiv shell"
        print("\n\nbye")
        return True

    def precmd(self, line):
        try:
            return self.command_alias[line]
        except KeyError:
            return line

    def postcmd(self, stop, line):
        # stop if we are called with commandline arguments
        if len(sys.argv)>1:
            stop = True
        return stop


class PyLucidEnvBuilder(venv.EnvBuilder):
    verbose = True

    def __init__(self, requirements):
        super().__init__(with_pip=True)
        self.requirements = requirements

    def ensure_directories(self, env_dir):
        print(" * Create the directories for the environment.")
        return super().ensure_directories(env_dir)

    def create_configuration(self, context):
        print(" * Create 'pyvenv.cfg' configuration file.")
        return super().create_configuration(context)

    def setup_python(self, context):
        print(" * Set up a Python executable in the environment.")
        return super().setup_python(context)

    def _setup_pip(self, context):
        print(" * Installs or upgrades pip in a virtual environment.")
        return super()._setup_pip(context)

    def setup_scripts(self, context):
        print(" * Set up scripts into the created environment.")
        return super().setup_scripts(context)

    def post_setup(self, context):
        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.

        :param context: The information for the virtual environment
                        creation request being processed.
        """
        print(" * post-setup modification")

        os.environ['VIRTUAL_ENV'] = context.env_dir

        pip3_path = Path(context.bin_path, "pip3")
        if not pip3_path.is_file():
            print("ERROR: pip not found here: '%s'" % pip3_path)
            return

        print("pip found here: '%s'" % pip3_path)
        context.pip3_path = str(pip3_path)

        verbose_check_call(context.pip3_path, "install", "--upgrade", "pip")

        args = [context.pip3_path, "install"] + self.requirements
        verbose_check_call(*args)


class PyLucidBootShell(Cmd2):

    #_________________________________________________________________________
    # Normal user commands:

    def _resolve_path(self, path):
        return Path(path).expanduser().resolve()

    def complete_boot(self, text, line, begidx, endidx):
        # print("text: %r" % text)
        # print("line: %r" % line)
        return self._complete_path(text, line, begidx, endidx)

    def _parse_requirements(self, requirement_string):
        requirements = []
        for line in requirement_string.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):

                line = line.split("# ", 1)[0] # Remove pip-compile comments e.g.: "... # via foo"
                line = line.rstrip()

                if line.startswith("-e"): # split editables
                    requirements += line.split(" ")
                else:
                    requirements.append(line)
        return requirements

    def _boot(self, destination, requirement_string):
        """
        Create a PyLucid virtualenv and install requirements.
        """
        requirements = self._parse_requirements(requirement_string)

        destination = Path(destination).expanduser().resolve()
        if destination.exists():
            self.stdout.write("\nERROR: Path '%s' already exists!\n" % destination)
            return

        self.stdout.write("Create virtualenv: '%s'...\n\n" % destination)

        builder = PyLucidEnvBuilder(requirements)
        builder.create(destination)

        self.stdout.write("\n")

        if not destination.is_dir():
            self.stdout.write("ERROR: Creating virtualenv!\n")
            return
        else:
            self.stdout.write("virtualenv created at: '%s'\n" % destination)

    def do_boot_normal(self, destination):
        """
        "normal" boot PyLucid

        usage:
            > boot_normal [path]

        Create a PyLucid virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/normal_installation.txt)
        """
        self._boot(destination, requirement_string=NORMAL_INSTALL_TXT)
    complete_boot_normal = complete_boot

    def do_boot_developer(self, destination):
        """
        **only usable for developer with github write access**
        (used the requirements/developer_installation.txt)
        """
        self._boot(destination, requirement_string=DEVELOPER_INSTALL_TXT)
    complete_boot_developer = complete_boot

    def do_boot_ci(self, destination):
        """
        **only for Travis CI**
        (used the requirements/ci_installation.txt)
        """
        self._boot(destination, requirement_string=CI_INSTALL_TXT)


def main():
    PyLucidBootShell().cmdloop()


if __name__ == '__main__':
    main()
