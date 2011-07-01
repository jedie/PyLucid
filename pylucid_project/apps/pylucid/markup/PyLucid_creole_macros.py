# coding: utf-8

"""
    PyLucid own creole2html macros
    
    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


# use all existing macros
try:
    # python-creole < v0.6
    from creole.default_macros import *
except ImportError:
    # python-creole >= v0.6
    from creole.shared.example_macros import *


from pylucid_project.apps.pylucid.markup.hightlighter import make_html


def code(ext, text):
    """
    Highlight sourcecode using
    Macro tag <<code ext=.EXT>>...<</code>>
    """
    try:
        source_type = ext.rsplit("=", 1)[-1]
    except (ValueError, IndexError):
        source_type = ""

    source_html = make_html(
        sourcecode=text, source_type=source_type, django_escape=True
    )
    return source_html
