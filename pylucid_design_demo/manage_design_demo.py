#!/usr/bin/env python
import os
import sys
import tempfile
import shutil
import atexit

TEMP_PATH_KEY="UNITTEST_TEMP_PATH"


def cleanup(temp_dir):
    if not os.path.isdir(temp_dir):
        return

    print("\nCleanup %r: " % temp_dir, end="")
    try:
        shutil.rmtree(temp_dir)
    except (OSError, IOError) as err:
        print("Error: %s" % err)
    else:
        print("OK")


def cli():
    # Use os.environ.setdefault here will call tempfile.mkdtemp even if key exists!
    # to avoid double temp dir creation, use this work-a-round:
    try:
        temp_dir = os.environ[TEMP_PATH_KEY]
    except KeyError:
        temp_dir = tempfile.mkdtemp(prefix="pylucid_design_demo_")
        os.environ[TEMP_PATH_KEY]=temp_dir

    os.environ['DJANGO_SETTINGS_MODULE'] = 'pylucid_design_demo.settings'
    print("Use DJANGO_SETTINGS_MODULE=%r" % os.environ["DJANGO_SETTINGS_MODULE"])

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

    # Register here, after the command call
    # so that this will not execute in the reload process:
    # print("\n +++ register cleanup at exit.")
    atexit.register(cleanup, temp_dir)


if __name__ == "__main__":
    cli()
