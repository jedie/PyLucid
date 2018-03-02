
import subprocess
import unittest
from pathlib import Path

# PyLucid
from pylucid.pylucid_admin import Requirements
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

    @unittest.skipIf(Requirements().normal_mode, "Only available in 'developer' mode.")
    def test_change_editable_address(self):
        """
        All test runs on Travis-CI install PyLucid as editable!
        See .travis.yml
        """
        req = Requirements()

        self.assertFalse(Requirements().normal_mode)

        pylucid_src_path = Path(req.src_path, "pylucid")
        print("pylucid_src_path: %r" % pylucid_src_path)

        self.assertTrue(pylucid_src_path.is_dir())
        self.assertTrue(str(pylucid_src_path).endswith("/src/pylucid"))

        git_path = Path(pylucid_src_path, ".git")
        print("git_path: %r" % git_path)

        self.assertTrue(git_path.is_dir())

        # Needed while developing with github write access url ;)
        output = VerboseSubprocess(
            "git", "remote", "set-url", "origin", "https://github.com/jedie/PyLucid.git",
            cwd=str(pylucid_src_path)
        ).verbose_output(check=True)
        # print(output)

        # Check if change was ok:
        output = VerboseSubprocess(
            "git", "remote", "-v",
            cwd=str(pylucid_src_path)
        ).verbose_output(check=True)
        # print(output)
        self.assertIn("https://github.com/jedie/PyLucid.git", output)
        self.assertNotIn("git@github.com", output)

        output = self.pylucid_admin_run("change_editable_address")
        print(output)

        self.assertIn("git@github.com:jedie/PyLucid.git", output)
