# coding: utf-8

"""
    unittest helper
    ~~~~~~~~~~~~~~~
    
    helper to run unittests.
    Add this to head of a unittest file, e.g:
    
    if __name__ == "__main__":
        # Run all unittest directly 
        from pylucid_project.tests import run_test_directly
        run_test_directly(__file__, verbosity=1, failfast=True)
        sys.exit()
    
    :copyleft: 2012-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


import os


def init_test_env():
    # the normal django settings module:
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid_project.settings"

    # test local settings should be used in pylucid_project.settings:
    os.environ["LOCAL_SETTINGS_MODULE"] = "pylucid_project.tests.tests_local_settings"

    os.environ["PYLUCID_UNITTESTS"] = "True"


def run_test_directly(*args, **kwargs):
    init_test_env()

    from django.core import management
    # management.call_command("diffsettings")
    management.call_command("test", *args, **kwargs)


if __name__ == "__main__":
    # Run all existing tests directly:
    run_test_directly()
