# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015-2018 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import pprint
import shutil
import subprocess
import tempfile
from unittest import TestCase

import sys


class BaseTestCase(TestCase):
    def subprocess_getstatusoutput(self, cmd, debug=False, **kwargs):
        """
        Return (status, output) of executing cmd in a shell.

        similar to subprocess.getstatusoutput but pass though kwargs
        """
        kwargs.update({
            "shell": True,
            "universal_newlines": True,
            "stderr": subprocess.STDOUT,
        })
        if "cwd" in kwargs:
            cwd = kwargs["cwd"]
            self.assertTrue(os.path.isdir(cwd), "cwd %r doesn't exists!" % cwd)
            if debug:
                print("DEBUG: cwd %r, ok" % cwd)

        # Assume that DJANGO_SETTINGS_MODULE not in environment
        # e.g:
        #   manage.py use os.environ.setdefault("DJANGO_SETTINGS_MODULE",...)
        #   so it will ignore the own module path!
        env=dict(os.environ)
        if "DJANGO_SETTINGS_MODULE" in env:
            del(env["DJANGO_SETTINGS_MODULE"])
        kwargs["env"] = env

        cmd=" ".join(cmd) # FIXME: Why?!?
        try:
            output = subprocess.check_output(cmd, **kwargs)
            status = 0
        except subprocess.CalledProcessError as ex:
            output = ex.output
            status = ex.returncode

        if output[-1:] == '\n':
            output = output[:-1]

        if status != 0 or debug:
            msg = (
                "subprocess exist status == %(status)r\n"
                "Call %(cmd)r with:\n"
                "%(kwargs)s\n"
                "subprocess output:\n"
                "------------------------------------------------------------\n"
                "%(output)s\n"
                "------------------------------------------------------------\n"
            ) % {
                "status": status,
                "cmd": cmd,
                "kwargs": pprint.pformat(kwargs),
                "output": output
            }
            if status != 0:
                raise AssertionError(msg)
            else:
                print(msg)

        return output

    # def call_manage_py(self, cmd, **kwargs):
    #     """
    #     call manage.py from pylucid_installer.page_instance_template.example_project
    #     """
    #     cmd = [sys.executable, "manage.py"] + list(cmd)
    #     kwargs.update({
    #         "cwd": os.path.abspath(os.path.join(os.path.dirname(example_project.__file__), "..")),
    #         #"debug": True,
    #     })
    #     return self.subprocess_getstatusoutput(cmd, **kwargs)


class IsolatedFilesystemTestCase(BaseTestCase):
    dont_cleanup_temp=False # Don't remove the creates temp files, for debugging only!

    def setUp(self):
        self._cwd = os.getcwd()
        self.temp_path = tempfile.mkdtemp(prefix="pylucid_unittest_%s_" % self._testMethodName)
        os.chdir(self.temp_path)

    def tearDown(self):
        os.chdir(self._cwd)
        if self.dont_cleanup_temp:
            print("WARNING: temp files %r will be not removed!" % self.temp_path)
            return

        try:
            shutil.rmtree(self.temp_path)
        except (OSError, IOError):
            pass


# class PageInstanceTestCase(IsolatedFilesystemTestCase):
#     """
#     -Create a page instance with the pylucid_installer cli
#     -run the test in the created page instance
#     """
#     def setUp(self):
#         super(PageInstanceTestCase, self).setUp()
#         runner = CliRunner()
#         result = runner.invoke(cli, [
#             "--dest", self.temp_path,
#             "--name", self._testMethodName,
#             "--remove"
#         ],
#             input="y"
#         )
#         # print(result.output)
#         self.project_path = os.path.join(self.temp_path, self._testMethodName)
#
#         self.assertIn(
#             "Rename '%s/example_project' to '%s'" % (
#                 self.temp_path, self.project_path
#             ),
#             result.output
#         )
#         self.assertIn(
#             "Page instance created here: '%s'" % self.temp_path,
#             result.output
#         )
#         self.assertNotIn("ERROR", result.output)
#         self.assertNotIn("The given project name is not useable!", result.output)
#         self.assertEqual(result.exit_code, 0)
#
#         self.assertTrue(os.path.isdir(self.project_path))
#
#         self.call_manage_py(["createcachetable"])
#
#     def call_manage_py(self, cmd, **kwargs):
#         """
#         Call manage.py from created page instance in temp dir.
#         """
#         cmd = ["./manage.py"] + list(cmd)
#         kwargs.update({
#             "cwd": self.temp_path,
#             # "debug": True,
#         })
#
#         # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.project_path, "settings.py")], **kwargs)
#         # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.temp_path, "manage.py")], **kwargs)
#         # self.subprocess_getstatusoutput(['python -c "import sys,pprint;pprint.pprint(sys.path)"'], **kwargs)
#
#         return self.subprocess_getstatusoutput(cmd, **kwargs)
