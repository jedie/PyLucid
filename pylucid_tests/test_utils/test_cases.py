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
import subprocess
from pathlib import Path
from unittest import TestCase

from pylucid.pylucid_boot import VerboseSubprocess
from pylucid_installer.pylucid_installer import create_instance

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


class BaseTestCase(TestCase):
    def subprocess_getstatusoutput(self, cmd, debug=False, **kwargs):
        """
        Return (status, output) of executing cmd in a shell.

        similar to subprocess.getstatusoutput but pass though kwargs
        """

        # TODO: Use pylucid.pylucid_boot.VerboseSubprocess !

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





@isolated_filesystem()
class PageInstanceTestCase(BaseTestCase):
    """
    -Create a page instance with the pylucid_installer cli
    -run the test in the created page instance
    """
    def setUp(self):
        super().setUp()

        self.temp_path = Path().cwd()  # isolated_filesystem does made a chdir to /tmp/...

        with StdoutStderrBuffer() as buffer:
            create_instance(
                dest = self.temp_path,
                name = self._testMethodName,
                remove = True,
                exist_ok = True,
            )

        output = buffer.get_output()

        # print(output)
        self.project_path = Path(self.temp_path, self._testMethodName)

        self.assertIn(
            "Rename '%s/example_project' to '%s'" % (
                self.temp_path, self.project_path
            ),
            output
        )
        self.assertIn(
            "Page instance created here: '%s'" % self.temp_path,
            output
        )
        self.assertNotIn("ERROR", output)
        self.assertNotIn("The given project name is not useable!", output)

        self.assertTrue(self.project_path.is_dir())

        self.createcachetable()

    def createcachetable(self):
        output = self.call_manage_py("createcachetable", "--verbosity", "3")
        print(output)
        self.assertIn("Cache table 'pylucid_cache_table' created.", output)

    def call_manage_py(self, *args, **kwargs):
        """
        Call manage.py from created page instance in temp dir.
        """
        args = ("./manage.py", ) + args
        kwargs.update({
            "cwd": str(self.temp_path),
        })
        return VerboseSubprocess(*args, **kwargs).verbose_output(check=False)

        # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.project_path, "settings.py")], **kwargs)
        # self.subprocess_getstatusoutput(["cat %s" % os.path.join(self.temp_path, "manage.py")], **kwargs)
        # self.subprocess_getstatusoutput(['python -c "import sys,pprint;pprint.pprint(sys.path)"'], **kwargs)


