# coding: utf-8

"""
    PyLucid own creole2html macros
    
    :copyleft: 2007-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""


# use all existing macros
try:
    # python-creole < v0.6
    from creole.default_macros import *
except ImportError:
    # python-creole >= v0.6
    from creole.shared.example_macros import *

TEMPLATE="""
{%% sourcecode ext="%s" %%}
%s
{%% endsourcecode %%}
"""

def code(ext, text):
    """
    Highlight sourcecode using
    Macro tag <<code ext=.EXT>>...<</code>>
    """
    try:
        source_type = ext.rsplit("=", 1)[-1]
    except (ValueError, IndexError):
        source_type = ""

    # return the django tag format, so we can parse it again in the same way ;)
    return TEMPLATE % (source_type, text)
