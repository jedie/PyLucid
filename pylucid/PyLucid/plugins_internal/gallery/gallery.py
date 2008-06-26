# -*- coding: utf-8 -*-

"""
    PyLucid gallery plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    a simple file/picture gallery

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev: 1634 $"

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Page, Plugin

class gallery(PyLucidBasePlugin):

    def lucidTag(self, name):
        # Get the preferences from the database:
        preferences = self.get_preferences(name)
        if preferences == None:
            # preferences not in database -> reinit required

