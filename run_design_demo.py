#!/usr/bin/env python3
# coding: utf-8

"""
    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function
import sys

from pylucid_design_demo.manage_design_demo import cli

if __name__ == "__main__":
    if len(sys.argv)==1:
        sys.argv.append("design_demo")
        
    cli()