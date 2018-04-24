#!/usr/bin/env python
import os
import sys
from pathlib import Path


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.resolve().parent)) # Hack
    # print("\n".join(sys.path))

    os.environ["DJANGO_SETTINGS_MODULE"]="pylucid_page_instance.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
