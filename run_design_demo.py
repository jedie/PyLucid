#!/usr/bin/env python
# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os

import django
from django.core.management import call_command

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pylucid_design_demo.settings'
    django.setup()

    call_command("design_demo")