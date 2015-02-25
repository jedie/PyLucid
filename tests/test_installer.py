from unittest import TestCase

from click.testing import CliRunner

from pylucid_installer.pylucid_installer import cli

class PyLucidInstallerCLITest(TestCase):
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage: cli [OPTIONS]", result.output)

