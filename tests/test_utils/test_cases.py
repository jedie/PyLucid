# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import shutil
import subprocess
import tempfile
from unittest import TestCase

from click.testing import CliRunner

from pylucid_installer.pylucid_installer import cli


class IsolatedFilesystemTestCase(TestCase):
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
        if debug:
            print("DEBUG: Call %r with: %r" % (cmd, kwargs))

        try:
            data = subprocess.check_output(cmd, **kwargs)
            status = 0
        except subprocess.CalledProcessError as ex:
            data = ex.output
            status = ex.returncode

        if data[-1:] == '\n':
            data = data[:-1]

        if debug:
            print("DEBUG subprocess status: %r" % status)
            print("DEBUG subprocess output:", data)

        return status, data


class PageInstanceTestCase(IsolatedFilesystemTestCase):
    def setUp(self):
        super(PageInstanceTestCase, self).setUp()
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--dest", self.temp_path,
            "--name", self._testMethodName,
            "--remove"
        ],
            input="y"
        )
        # print(result.output)
        self.project_path = os.path.join(self.temp_path, self._testMethodName)

        self.assertIn(
            "Rename '%s/example_project' to '%s'" % (
                self.temp_path, self.project_path
            ),
            result.output
        )
        self.assertIn(
            "Page instance created here: '%s'" % self.temp_path,
            result.output
        )
        self.assertNotIn("ERROR", result.output)
        self.assertNotIn("The given project name is not useable!", result.output)
        self.assertEqual(result.exit_code, 0)

        self.assertTrue(os.path.isdir(self.project_path))

    def call_manage_py(self, cmd, **kwargs):
        cmd = ["./manage.py"] + list(cmd)
        kwargs.update({"cwd": self.temp_path})

        # kwargs["debug"] = True
        # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.project_path, "settings.py")], **kwargs)
        # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.temp_path, "manage.py")], **kwargs)
        # self.subprocess_getstatusoutput(['python -c "import sys,pprint;pprint.pprint(sys.path)"'], **kwargs)

        return self.subprocess_getstatusoutput(cmd, **kwargs)