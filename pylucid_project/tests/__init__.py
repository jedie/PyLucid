# coding: utf-8


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
    management.call_command("test", *args, **kwargs)