# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os

from django.core.management import call_command, BaseCommand
from pylucid_design_demo.dummy_data import create_pages, create_test_user


class Command(BaseCommand):
    help = 'run dev server with in-memory design demo page'
    def handle(self, *args, **options):
        """
        INFO: The django reloader will call this multiple times!
        We check RUN_MAIN, that will be set in django.utils.autoreload
        So we can skip the first migrate run.
        """
        self.stdout.write("\n")
        if os.environ.get("RUN_MAIN", None) is not None:
            print("\n *** call 'migrate' command:")
            call_command("migrate", interactive=False, verbosity=1)

            create_pages()
            create_test_user()

        print("\n *** call 'runserver' command:")
        call_command("runserver",
             use_threading=False,
             use_reloader=True  ,
             verbosity=2
        )
