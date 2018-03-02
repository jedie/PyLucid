
import subprocess
import unittest

# PyLucid
from pylucid.pylucid_boot import VerboseSubprocess


class TestPyLucidAdmin(unittest.TestCase):
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
            self.fail("Subprocess error: %s" % err)

    def test_help(self):
        output = self.pylucid_admin_run("help")
        print(output)

        self.assertIn("pylucid_boot.py shell", output)
        self.assertIn("Documented commands (type help <topic>):", output)
        self.assertIn("boot", output)
        self.assertIn("boot_developer", output)

        # If DocString is missing in do_<name>():
        self.assertNotIn("Undocumented commands", output)
