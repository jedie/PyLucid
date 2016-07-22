# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

from django.conf import settings
from django.contrib.auth.models import User
from django.db.utils import OperationalError

from django.core.management import call_command
from django.core.management.commands.runserver import Command as RunServerCommand
from pylucid_design_demo.dummy_data import create_pages, create_test_user


class Command(RunServerCommand):
    help = 'run dev server with in-memory design demo page'
    def check_migrations(self):
        try:
            user_exists = User.objects.filter(username=settings.TEST_USERNAME).exists()
        except OperationalError as err:
            print(err)
            user_exists = False

        if user_exists:
            print("\n *** Skip migrate/test data creations...")
        else:
            print("\n *** call 'migrate' command:")

            call_command("migrate", interactive=False, verbosity=1)

            create_pages()
            create_test_user()

