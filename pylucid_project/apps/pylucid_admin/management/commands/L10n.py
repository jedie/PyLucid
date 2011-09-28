# coding: utf-8

"""
    PyLucid managment command
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    make-/compile-messages for pylucid apps
    
    see also: http://www.pylucid.org/permalink/314/how-to-localize-pylucid
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import traceback
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.compilemessages import compile_messages
from django.core.management.commands.makemessages import make_messages
from django.utils.importlib import import_module


OWN_PROJECTS = (
    "pylucid_project",
    "django_processinfo",
    "dbpreferences",
)
MAKE_MESSAGES = "make"
COMPILE_MESSAGES = "compile"


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--locale', '-l', default=None, dest='locale',
            help='Creates or updates the message files for the given locale (e.g. pt_BR) or for all.'),
    )
    help = (
        'Creates (or updates) .po messages'
        ' or compiles .po files to .mo files'
        ' for use with builtin gettext support.'
    )
    args = "%s/%s [app_name-1, app_name-2 ... app_name-n]" % (MAKE_MESSAGES, COMPILE_MESSAGES)



    requires_model_validation = False
    can_import_settings = False

    def _pylucid_app_names(self):
        def is_own_project(app_name):
            for own_project in OWN_PROJECTS:
                if own_project in app_name:
                    return True
            return False

        app_names = [n for n in settings.INSTALLED_APPS if is_own_project(n)]
        return app_names

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))
        locale = options.get('locale')
        if locale is None:
            process_all = True
        else:
            process_all = False

        if len(args) == 0:
            raise CommandError("missing '%s' or '%s' argument!" % (MAKE_MESSAGES, COMPILE_MESSAGES))

        cmd_type = args[0]
        if cmd_type not in (MAKE_MESSAGES, COMPILE_MESSAGES):
            raise CommandError("First argument must be '%s' or '%s' !" % (MAKE_MESSAGES, COMPILE_MESSAGES))

        pylucid_app_names = self._pylucid_app_names()

        if len(args) > 1:
            only_apps = args[1:]
            sys.stdout.write("%s only the apps: %s" % (cmd_type, repr(only_apps)))

            app_names = []
            for app_name in only_apps:
                if app_name in pylucid_app_names:
                    app_names.append(app_name)
                else:
                    app_name = ".%s" % app_name
                    full_app_name = None
                    for app_name2 in pylucid_app_names:
                        if app_name2.endswith(app_name):
                            full_app_name = app_name2
                            break
                    if full_app_name is None:
                        sys.stderr.write("App with name %r is unknown or not a PyLucid app!" % app_name)
                    else:
                        app_names.append(full_app_name)
            if not app_names:
                raise CommandError("No valid PyLucid apps found!")
        else:
            app_names = pylucid_app_names

        for app_name in app_names:
            print "_"*79
            print "%s: %s" % (cmd_type, app_name)
            app_module = import_module(app_name)
            app_path = os.path.dirname(app_module.__file__)

            os.chdir(app_path)

            if cmd_type == COMPILE_MESSAGES:
                try:
                    compile_messages(self.stderr)
                except Exception:
                    print traceback.format_exc()
            elif cmd_type == MAKE_MESSAGES:
                try:
                    make_messages(
                        locale=locale,
                        domain="django",
                        verbosity=self.verbosity,
                        all=process_all,
                        extensions=[".html", ],
                        symlinks=True,
                        ignore_patterns=['CVS', '.*', '*~'],
                        no_wrap=False,
                        no_obsolete=True,
                    )
                except Exception:
                    print traceback.format_exc()
            else:
                raise

