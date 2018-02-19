#!/usr/bin/python3

"""
    PyLucid Admin
    ~~~~~~~~~~~~~

    A interactive admin for PyLucid.

    usage, e.g.:

        $ wget https://raw.githubusercontent.com/jedie/PyLucid/pylucid_v3/pylucid/pylucid_admin.py
        $ python3 pylucid_admin.py

        pylucid_admin.py> boot ~/PyLucid_env


    :created: 08.02.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

import cmd
import glob
import logging
import os
import re
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

SELF_FILENAME=os.path.basename(__file__)
SELF_FILEPATH=Path(__file__).resolve()

# The following Variables CI_INSTALL_TXT, DEVELOPER_INSTALL_TXT and NORMAL_INSTALL_TXT are filled
# automatically from the requirements files on:
#   PyLucidShell.do_upgrade_requirements()
# by
#
# $ ./pylucid.py upgrade_requirements

# Helper to replace the content:
INSERT_START_RE=re.compile(r'(?P<variable>.*?)=""" # insert \[(?P<filename>.*?)\]')
INSERT_END = '"""'

CI_INSTALL_TXT=""" # insert [../requirements/ci_installation.txt]
-e git+https://github.com/jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+https://github.com/jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+https://github.com/jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+https://github.com/jedie/PyLucid.git@develop#egg=pylucid
aldryn-apphooks-config==0.3.3  # via djangocms-blog
aldryn-boilerplates==0.7.5  # via aldryn-common
aldryn-common==1.0.4      # via aldryn-search
aldryn-search==0.4.1      # via djangocms-blog
certifi==2018.1.18        # via requests
chardet==3.0.4            # via requests
click==6.6
cmsplugin-filer==1.1.3
cmsplugin-pygments==0.8.2
coverage==4.5.1           # via coveralls
coveralls==1.2.0
django-appconf==1.0.2     # via aldryn-boilerplates, aldryn-search, cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai, django-standard-form
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar-django-info==0.3.0
django-debug-toolbar==1.5
django-filer==1.2.8
django-formtools==2.1     # via django-cms
django-haystack==2.7.0    # via aldryn-search
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.0.2  # via django-filer
django-reversion-compare==0.6.3
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via aldryn-common
django-spurl==0.6.4       # via aldryn-search
django-standard-form==1.1.1  # via aldryn-search
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-tools==0.30.4
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.8.13
djangocms-htmlsitemap==0.2.0
docopt==0.6.2             # via coveralls
docutils==0.14
easy-thumbnails==2.3      # via cmsplugin-filer, django-filer
html5lib==1.0.1           # via textile
idna==2.6                 # via requests
lxml==4.1.1               # via aldryn-search
markdown==2.6.11
pillow==5.0.0
pygments==2.1.3
python-creole==1.3.1
pytz==2018.3
rcssmin==1.0.6            # via django-compressor
requests==2.18.4          # via coveralls
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via aldryn-common, django-spurl, html5lib, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
unidecode==0.4.21         # via django-filer
urllib3==1.22             # via requests
urlobject==2.4.3          # via django-spurl
webencodings==0.5.1       # via html5lib
yurl==0.13                # via aldryn-boilerplates
"""

DEVELOPER_INSTALL_TXT=""" # insert [../requirements/developer_installation.txt]
-e git+git@github.com:jedie/bootstrap_env.git#egg=bootstrap_env
-e git+git@github.com:jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+git@github.com:jedie/cmsplugin-pygments.git#egg=cmsplugin-pygments
-e git+git@github.com:jedie/django-debug-toolbar-django-info.git#egg=django-debug-toolbar-django-info
-e git+git@github.com:jedie/django-reversion-compare.git@stable/v0.6.x#egg=django-reversion-compare
-e git+git@github.com:jedie/django-tools.git@master#egg=django-tools
-e git+git@github.com:jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+git@github.com:jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+git@github.com:jedie/PyLucid.git@pylucid_v3#egg=pylucid
-e git+git@github.com:jedie/python-creole.git#egg=python-creole
aldryn-apphooks-config==0.3.3  # via djangocms-blog
aldryn-boilerplates==0.7.5  # via aldryn-common
aldryn-common==1.0.4      # via aldryn-search
aldryn-search==0.4.1      # via djangocms-blog
certifi==2018.1.18        # via requests
chardet==3.0.4            # via requests
click==6.6
cmsplugin-filer==1.1.3
django-appconf==1.0.2     # via aldryn-boilerplates, aldryn-search, cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai, django-standard-form
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar==1.5
django-extensions==1.9.9
django-filer==1.2.8
django-formtools==2.1     # via django-cms
django-haystack==2.7.0    # via aldryn-search
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.0.2  # via django-filer
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via aldryn-common
django-spurl==0.6.4       # via aldryn-search
django-standard-form==1.1.1  # via aldryn-search
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.8.13
djangocms-htmlsitemap==0.2.0
docutils==0.14
easy-thumbnails==2.3      # via cmsplugin-filer, django-filer
first==2.0.1              # via pip-tools
html5lib==1.0.1           # via textile
idna==2.6                 # via requests
lxml==4.1.1               # via aldryn-search
markdown==2.6.11
pillow==5.0.0
pip-tools==1.11.0
piprot==0.9.7
pkginfo==1.4.1            # via twine
pygments==2.1.3
pytz==2018.3
rcssmin==1.0.6            # via django-compressor
requests-futures==0.9.7   # via piprot
requests-toolbelt==0.8.0  # via twine
requests==2.18.4          # via piprot, requests-futures, requests-toolbelt, twine
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via aldryn-common, django-extensions, django-spurl, html5lib, pip-tools, piprot, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
tqdm==4.19.5              # via twine
twine==1.9.1
typing==3.6.4             # via django-extensions
unidecode==0.4.21         # via django-filer
urllib3==1.22             # via requests
urlobject==2.4.3          # via django-spurl
virtualenv==15.1.0
webencodings==0.5.1       # via html5lib
werkzeug==0.14.1
wheel==0.30.0
yurl==0.13                # via aldryn-boilerplates
"""

NORMAL_INSTALL_TXT=""" # insert [../requirements/developer_installation.txt]
-e git+git@github.com:jedie/bootstrap_env.git#egg=bootstrap_env
-e git+git@github.com:jedie/cmsplugin-markup.git@develop#egg=cmsplugin-markup
-e git+git@github.com:jedie/cmsplugin-pygments.git#egg=cmsplugin-pygments
-e git+git@github.com:jedie/django-debug-toolbar-django-info.git#egg=django-debug-toolbar-django-info
-e git+git@github.com:jedie/django-reversion-compare.git@stable/v0.6.x#egg=django-reversion-compare
-e git+git@github.com:jedie/django-tools.git@master#egg=django-tools
-e git+git@github.com:jedie/djangocms-text-ckeditor.git@update_html5lib#egg=djangocms-text-ckeditor
-e git+git@github.com:jedie/djangocms-widgets.git#egg=djangocms-widgets
-e git+git@github.com:jedie/PyLucid.git@pylucid_v3#egg=pylucid
-e git+git@github.com:jedie/python-creole.git#egg=python-creole
aldryn-apphooks-config==0.3.3  # via djangocms-blog
aldryn-boilerplates==0.7.5  # via aldryn-common
aldryn-common==1.0.4      # via aldryn-search
aldryn-search==0.4.1      # via djangocms-blog
certifi==2018.1.18        # via requests
chardet==3.0.4            # via requests
click==6.6
cmsplugin-filer==1.1.3
django-appconf==1.0.2     # via aldryn-boilerplates, aldryn-search, cmsplugin-filer, django-compressor
django-appdata==0.1.6     # via aldryn-apphooks-config
django-classy-tags==0.8.0  # via django-cms, django-sekizai, django-standard-form
django-cms==3.4.5
django-compressor==2.1.1
django-debug-toolbar==1.5
django-extensions==1.9.9
django-filer==1.2.8
django-formtools==2.1     # via django-cms
django-haystack==2.7.0    # via aldryn-search
django-meta-mixin==0.3.0  # via djangocms-blog
django-meta==1.4.1        # via django-meta-mixin, djangocms-blog
django-mptt==0.8.7        # via django-filer
django-parler==1.9.2      # via djangocms-blog
django-polymorphic==1.0.2  # via django-filer
django-reversion==1.10.2
django-sekizai==0.10.0    # via cmsplugin-filer, django-cms, django-meta-mixin
django-sortedm2m==1.5.0   # via aldryn-common
django-spurl==0.6.4       # via aldryn-search
django-standard-form==1.1.1  # via aldryn-search
django-taggit-autosuggest==0.3.2  # via djangocms-blog
django-taggit-templatetags==0.2.5  # via djangocms-blog
django-taggit==0.22.2     # via django-taggit-autosuggest, django-taggit-templatetags, djangocms-blog
django-templatetag-sugar==1.0  # via django-taggit-templatetags
django-treebeard==4.2.0   # via django-cms
django==1.9.13
djangocms-admin-style==1.2.7  # via django-cms
djangocms-apphook-setup==0.3.0  # via djangocms-blog
djangocms-attributes-field==0.3.0  # via cmsplugin-filer
djangocms-blog==0.8.13
djangocms-htmlsitemap==0.2.0
docutils==0.14
easy-thumbnails==2.3      # via cmsplugin-filer, django-filer
first==2.0.1              # via pip-tools
html5lib==1.0.1           # via textile
idna==2.6                 # via requests
lxml==4.1.1               # via aldryn-search
markdown==2.6.11
pillow==5.0.0
pip-tools==1.11.0
piprot==0.9.7
pkginfo==1.4.1            # via twine
pygments==2.1.3
pytz==2018.3
rcssmin==1.0.6            # via django-compressor
requests-futures==0.9.7   # via piprot
requests-toolbelt==0.8.0  # via twine
requests==2.18.4          # via piprot, requests-futures, requests-toolbelt, twine
rjsmin==1.0.12            # via django-compressor
six==1.11.0               # via aldryn-common, django-extensions, django-spurl, html5lib, pip-tools, piprot, textile
sqlparse==0.2.4           # via django-debug-toolbar
textile==3.0.0
tqdm==4.19.5              # via twine
twine==1.9.1
typing==3.6.4             # via django-extensions
unidecode==0.4.21         # via django-filer
urllib3==1.22             # via requests
urlobject==2.4.3          # via django-spurl
virtualenv==15.1.0
webencodings==0.5.1       # via html5lib
werkzeug==0.14.1
wheel==0.30.0
yurl==0.13                # via aldryn-boilerplates
"""


class Requirement:
    """
    Helper class to insert requirements/*_installation.txt file content.
    """
    def parse_req_file(self, req_file):
        """
        returns the lines of a requirements/*_installation.txt file.
        Skip comments and emptry lines
        """
        lines = []
        print("read %r..." % req_file)
        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                assert not line.startswith("-r"), "'-r' not supported! Not the pip-compile output file?!?"
                lines.append("%s\n" % line)

        return lines

    def update(self):
        new_content = []
        with open(SELF_FILEPATH, "r") as f:
            in_insert_block=False
            for line in f:
                if not in_insert_block:
                    new_content.append(line)

                if in_insert_block:
                    if line.strip() == INSERT_END:
                        in_insert_block=False
                        new_content.append(line)

                else:
                    m = INSERT_START_RE.match(line)
                    if m:
                        in_insert_block=True
                        m = m.groupdict()
                        variable = m["variable"]
                        filename = m["filename"]
                        print("Fill %r from %r..." % (variable, filename))
                        new_content += self.parse_req_file(filename)


        bak_filename=Path("%s.bak" % SELF_FILEPATH)
        if bak_filename.is_file():
            print("Remove old backup file: %s" % bak_filename)
            bak_filename.unlink()

        print("Create backup file: %r" % bak_filename)
        SELF_FILEPATH.rename(bak_filename)

        with open(SELF_FILEPATH, "w") as f:
            f.writelines(new_content)

        SELF_FILEPATH.chmod(0o775)


def verbose_check_call(*args):
    """
    'verbose' version of subprocess.check_output()
    """
    print("Call: %r" % " ".join(args))
    try:
        subprocess.check_call(args, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise


def iter_subprocess_output(args):
    """
    A subprocess with tee ;)
    """
    print("Call: %s" % " ".join(args))

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"]="1" # If a python script called ;)

    proc=subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=1, env=env, universal_newlines=True,
    )
    return iter(proc.stdout.readline,'')


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
    command_alias = { # used in self.precmd()
        "q": "quit", "EOF": "quit",
        "--help": "help", "-h": "help", "-?": "help",
    }

    intro = (
        '\n{filename} shell v{version}\n'
        'Type help or ? to list commands.\n'
    ).format(
        filename=SELF_FILENAME,
        version=__version__
    )

    prompt = '%s> ' % SELF_FILENAME

    doc_leader = (
        "\nHint: All commands can be called directly from commandline.\n"
        "e.g.: $ ./{filename} pip_freeze\n"
    ).format(
        filename=SELF_FILENAME,
    )

    # Will be append to 'doc_leader' in self.do_help():
    complete_hint="\nUse <{key}> to command completion.\n"
    missing_complete="\n(Sorry, no command completion available.)\n" # if 'readline' not available

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        verbose_check_call(context.pip3_path, "install", "django<2.0")




class PyLucidShell(Cmd2):

    #_________________________________________________________________________
    # Normal user commands:

    def _resolve_path(self, path):
        return Path(path).expanduser().resolve()

    def complete_boot(self, text, line, begidx, endidx):
        return self._complete_path(text, line, begidx, endidx)

    def do_boot(self, destination):
        """
        usage:
            > boot [path]

        Create a PyLucid virtualenv in the given [path].
        The destination path must not exist yet!
        """
        destination = Path(destination).expanduser().resolve()
        if destination.exists():
            self.stdout.write("\nERROR: Path '%s' already exists!\n" % destination)
            return

        self.stdout.write("Create virtualenv: '%s'...\n\n" % destination)

        builder = PyLucidEnvBuilder(with_pip=True)
        builder.create(destination)

        self.stdout.write("\n")

        if not destination.is_dir():
            self.stdout.write("ERROR: Creating virtualenv!\n")
            return
        else:
            self.stdout.write("virtualenv created at: '%s'\n" % destination)

    #_________________________________________________________________________
    # Developer commands:

    def do_insert_requirement(self, arg):
        """
        insert requirements/*_installation.txt files into pylucid/pylucid_admin.py
        This will be automaticly done by 'upgrade_requirements'!
        """
        Requirement().update()

    def do_upgrade_requirements(self, arg):
        """
        Convert via 'pip-compile' *.in requirements files to *.txt
        Append 'piprot' informations to *.txt requirements.

        Direct start with:
            $ ./pylucid.py upgrade_requirements
        """
        for requirement_in in glob.glob(os.path.join("requirements", "*.in")):
            if "basic_" in requirement_in:
                continue
            requirement_out = requirement_in.replace(".in", ".txt")

            self.stdout.write("_"*79 + "\n")
            verbose_check_call("pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in)

            self.stdout.write("_"*79 + "\n")
            args = ["piprot", "--outdated", requirement_out]
            output = [
                "\n#\n# list of out of date packages made with piprot:\n#\n"
            ]
            for line in iter_subprocess_output(args):
                self.stdout.write(line)
                self.stdout.flush()
                output.append("# %s" % line)

            self.stdout.write("\nUpdate file %r\n" % requirement_out)
            with open(requirement_out, "a") as f:
                f.writelines(output)

        self.do_insert_requirement(arg)

    def _install(self, requirements_filename):
        verbose_check_call("pip3", "install", "--upgrade", "pip")
        requirement = os.path.join("requirements", requirements_filename)
        verbose_check_call("pip3", "install", "-r", requirement)

    def do_install_normal(self, arg):
        """
        pip install -r normal_installation.txt

        The "normal" way for all PyLucid users:
        Use PyPi packages and read-only sources from github.
        """
        self._install("normal_installation.txt")

    def do_install_developer(self, arg):
        """
        pip install -r developer_installation.txt

        **only usable for developer with github write access**
        """
        self._install("developer_installation.txt")

    def do_install_ci(self, arg):
        """
        pip install -r ci_installation.txt

        **only for Travis CI**
        """
        self._install("ci_installation.txt")

    def do_pip_freeze(self, arg):
        "run 'pip freeze': FOO"
        verbose_check_call("pip3", "freeze")


def main():
    PyLucidShell().cmdloop()


if __name__ == '__main__':
    main()
