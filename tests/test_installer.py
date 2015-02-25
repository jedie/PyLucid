import os
from unittest import TestCase
import sys

from click.testing import CliRunner

from pylucid_installer.pylucid_installer import cli


class PyLucidInstallerCLITest(TestCase):
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage: cli [OPTIONS]", result.output)
        # print(result.output)

    def test_dest_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as temp_path:
            result = runner.invoke(cli, [
                "--dest", temp_path,
                "--name", "test_remove_question",
            ])
            # print(result.output)
            self.assertIn("ERROR: Destination '%s' exist!" % temp_path, result.output)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(os.listdir(temp_path), [])

    def test_remove_question(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as temp_path:
            result = runner.invoke(cli, [
                "--dest", temp_path,
                "--name", "test_remove_question",
                "--remove"
            ])
            # print(result.output)
            self.assertIn(
                "Delete '%s' before copy? [y/N]:" % temp_path,
                result.output
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(os.listdir(temp_path), [])

    def test_create(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as temp_path:
            result = runner.invoke(cli, [
                "--dest", temp_path,
                "--name", "unittest_project",
                "--remove"
            ],
                input="y"
            )
            # print(result.output)
            self.assertIn(
                "Delete '%s' before copy? [y/N]:" % temp_path,
                result.output
            )
            self.assertEqual(result.exit_code, 0)

            self.assertIn(
                "Page instance created here: '%s'" % temp_path,
                result.output
            )
            self.assertEqual(
                os.listdir(temp_path),
                ['static', 'manage.py', 'unittest_project']
            )

            # Check patched manage.py
            with open(os.path.join(temp_path, "manage.py"), "r") as f:
                shebang = f.readlines(1)
                self.assertEqual(shebang, ["#!%s\n" % sys.executable])

                content = f.read()
                # print(content)
                self.assertIn(
                    'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unittest_project.settings")',
                    content
                )

            # Check patched settings.py
            with open(os.path.join(temp_path, "unittest_project", "settings.py"), "r") as f:
                content = f.read()
                # print(content)
                self.assertIn(
                    'DOC_ROOT = "%s"' % temp_path,
                    content
                )
                self.assertIn(
                    "ROOT_URLCONF = 'unittest_project.urls'",
                    content
                )