#!/usr/bin/env python

import os
import sys

if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    print("(Current Python Version is %s)\n" % sys.version.split(" ", 1)[0])
    sys.exit(101)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")
    # print("Use DJANGO_SETTINGS_MODULE=%r" % os.environ["DJANGO_SETTINGS_MODULE"])

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
