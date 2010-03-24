# -*- coding: utf-8 -*-

"""
    PyLucid own creole2html macros
"""

# use all existing macros
from creole.default_macros import *

from pylucid_project.apps.pylucid.markup.hightlighter import make_html

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
