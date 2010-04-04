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
    try:
        source_type = args.rsplit("=", 1)[-1]
    except (ValueError, IndexError):
        source_type = ""

    source_html = make_html(
        sourcecode=text, source_type=source_type, django_escape=True
    )
    return source_html
