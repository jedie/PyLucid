
import subprocess
import unittest
from pathlib import Path

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem

# PyLucid
from pylucid.pylucid_boot import VerboseSubprocess


class TestPyLucidBoot(unittest.TestCase):
    """
    Tests for pylucid/pylucid_boot.py

    Note: Travis-CI used pylucid_boot.py to bootstrap into "normal" and "develop" mode!
        No need to test is here again ;)
        Unfortunately, however, the coverage for bootstrapping are missing.
    """
    def pylucid_admin_run(self, *args):
        args = ("pylucid_boot", ) + args
        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            print(err.output)
            self.fail("Subprocess error: %s" % err)

    def test_help(self):
        output = self.pylucid_admin_run("help")
        print(output)

        self.assertIn("pylucid_boot.py shell", output)
        self.assertIn("Available commands (type help <topic>):", output)

        self.assertIn("boot", output)
        self.assertIn('Bootstrap PyLucid virtualenv in "normal" mode.', output)

        self.assertIn("boot_developer", output)
        self.assertIn('Bootstrap PyLucid virtualenv in "developer" mode.', output)

        # If DocString is missing in do_<name>():
        self.assertNotIn("Undocumented", output)

    def test_boot_into_existing_path(self):
        with isolated_filesystem():
            temp_path = Path().cwd() # isolated_filesystem does made a chdir to /tmp/...

            with self.assertRaises(subprocess.CalledProcessError) as cm:
                VerboseSubprocess("pylucid_boot", "boot", str(temp_path)).verbose_output(check=False)

            caller_process_error = cm.exception
            output = caller_process_error.output
            print(output)

            self.assertIn("ERROR: Path '%s' already exists!" % temp_path, output)
