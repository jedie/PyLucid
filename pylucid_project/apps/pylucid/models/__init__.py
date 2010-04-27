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


# Add a entry into update journal
signals.post_save.connect(receiver=update_journal.save_receiver, sender=PageContent)

