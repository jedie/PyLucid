# coding: utf-8

"""
    PyLucid.models
    ~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db.models import signals

from colorscheme import ColorScheme, Color
from design import Design
from editable_headfile import EditableHtmlHeadFile
from ip_ban_list import BanEntry
from language import Language
from log import LogEntry
from pagecontent import PageContent
from pagemeta import PageMeta
from pagetree import PageTree
from pluginpage import PluginPage
from userprofile import UserProfile

from pylucid_project.pylucid_plugins import update_journal
from pylucid_project.apps.pylucid.cache import clean_complete_pagecache


# Add a entry into update journal
signals.post_save.connect(receiver=update_journal.save_receiver, sender=PageContent)

# For cleaning the page cache:
signals.post_save.connect(receiver=clean_complete_pagecache, sender=PageTree)
signals.post_save.connect(receiver=clean_complete_pagecache, sender=PageMeta)
signals.post_save.connect(receiver=clean_complete_pagecache, sender=PageContent)
signals.post_save.connect(receiver=clean_complete_pagecache, sender=PluginPage)
signals.post_save.connect(receiver=clean_complete_pagecache, sender=EditableHtmlHeadFile)
