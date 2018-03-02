
import unittest

import subprocess

from pylucid.pylucid_boot import VerboseSubprocess

class TestPyLucidAdmin(unittest.TestCase):
    """
    Tests for pylucid/pylucid_admin.py
    """
    def pylucid_admin_run(self, *args):
        args = ("pylucid_admin", ) + args
        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            self.fail("Subprocess error: %s" % err)

    def test_help(self):
        output = self.pylucid_admin_run("help")
        print(output)

        self.assertIn("pylucid_admin.py shell", output)
        self.assertIn("Documented commands (type help <topic>):", output)
        self.assertIn("create_page_instance", output)
        self.assertIn("update_env", output)

        # If DocString is missing in do_<name>():
        self.assertNotIn("Undocumented commands", output)
