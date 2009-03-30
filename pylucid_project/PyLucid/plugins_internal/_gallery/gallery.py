# -*- coding: utf-8 -*-

"""
    PyLucid gallery plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    a simple file/picture gallery

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

import os

from PyLucid.system.BaseFilesystemPlugin import FilesystemPlugin
from PyLucid.models import Page, Plugin

class gallery(FilesystemPlugin):

    def lucidTag(self, base_path="0", id=None):
        # Get the preferences from the database:
        preferences = self.get_preferences(id)
        if preferences == None:
            # preferences not in database -> reinit required
            self.page_msg("No preferences!")
            return
        
        self.page_msg(preferences)
        
        preferences["base_path"]
        
        # analyse and store the given GET path infomation
#        self.path.new_dir_path(path_info, must_exist=True)
        #self.path.debug()
        