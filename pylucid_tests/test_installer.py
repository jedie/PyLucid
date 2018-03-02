# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015-2018 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
from pathlib import Path
from unittest import TestCase

from django.utils.version import get_main_version

from pylucid_installer.pylucid_installer import create_instance, get_python3_shebang
from pylucid_tests.test_utils.test_cases import BaseTestCase, PageInstanceTestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

# PyLucid
from pylucid.pylucid_boot import VerboseSubprocess


@isolated_filesystem()
class PyLucidInstallerTest(BaseUnittestCase):
    def setUp(self):
        super().setUp()
        self.temp_path = Path().cwd()  # isolated_filesystem does made a chdir to /tmp/...

    def test_create(self):
        destination = Path(self.temp_path, self._testMethodName)
        self.assertFalse(destination.is_dir())

        output = VerboseSubprocess(
            "pylucid_admin", "create_page_instance", str(destination), self._testMethodName
        ).verbose_output(check=False)

        print(output)

        self.assertIn(
            "Page instance created here: '%s'" % destination,
            output
        )
        self.assertEqual(
            set([p.name for p in destination.iterdir()]),
            {'manage.py', 'media', 'static', self._testMethodName}
        )

        # Check patched manage.py
        with Path(destination, "manage.py").open("r") as f:
            shebang = f.readlines(1)[0]

            self.assertEqual(shebang, "%s\n" % get_python3_shebang())

            content = f.read()
            print(content)
            self.assertIn(
                'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings")' % self._testMethodName,
                content
            )

        # Check patched settings.py
        with Path(destination, self._testMethodName, "settings.py").open("r") as f:
            content = f.read()
            print(content)
            self.assertIn(
                'DOC_ROOT = "%s"' % destination,
                content
            )
            self.assertIn(
                'ROOT_URLCONF = "%s.urls"' % self._testMethodName,
                content
            )


class ManageTest(PageInstanceTestCase):
    # def test_debug_settings(self):
    #     with open(os.path.join(self.project_path, "settings.py"), "r") as f:
    #         content = f.read()
    #         print(content)

    def test_help(self):
        output = self.call_manage_py("--help")
        # print(output)

        self.assertIn("Type 'manage.py help <subcommand>' for help on a specific subcommand.", output)
        self.assertNotIn("Warning:", output)

    def test_check(self):
        output = self.call_manage_py("check")
        self.assertNotIn("ImproperlyConfigured", output)

    def test_diffsettings(self):
        # self.dont_cleanup_temp=True

        output = self.call_manage_py("diffsettings")
        print(output)
        self.assertNotIn("ImproperlyConfigured", output)
        # self.assertIn(
        #     "DOC_ROOT = '%s'" % self.project_path,
        #     output
        # )
        self.assertIn(
            "STATIC_ROOT = '%s'" % Path(self.instance_root, "static"),
            output
        )
        self.assertIn(
            "MEDIA_ROOT = '%s'" % Path(self.instance_root, "media"),
            output
        )

    def test_migrate(self):
        output = self.call_manage_py("migrate", "--noinput")
        print(output)
        self.assertIn("Running migrations:", output)
        self.assertIn("Applying auth.", output)
        self.assertIn("Applying cms.", output)
        self.assertIn("Applying djangocms_blog.", output)
