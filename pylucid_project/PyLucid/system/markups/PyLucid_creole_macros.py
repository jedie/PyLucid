# -*- coding: utf-8 -*-

"""
    PyLucid own creole2html macros
"""

from PyLucid.system.hightlighter import make_html

# use all existing macros
from PyLucid.system.markups.creole.default_macros import *

def code(args, text):
    """
    Highlight sourcecode using
    Macro tag <<code ext=.EXT>>...<</code>>
    """
    if "=" in args:
        source_type = args.split("=")[-1].strip("\" '")
        if not source_type.startswith("."):
            source_type = ".%s" % source_type
    else:
        source_type = ""

    return make_html(
        sourcecode = text,
        source_type=source_type,
    )
