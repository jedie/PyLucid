# -*- coding: utf-8 -*-

"""
    response tools
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings


class SimpleStringIO(object):
    """
    Minimalistic StringIO-file-like object.
    Encode unicode to the default charset (imported from the settings).
    See http://docs.python.org/lib/bltin-file-objects.html
    """
    def __init__(self):
        self._charset = settings.DEFAULT_CHARSET
        self._container = []

    def write(self, content):
        """
        Append a new chunk.
        Encode unicode to the default charset.
        """
        if isinstance(content, unicode):
            content = content.encode(self._charset)
        self._container.append(content)

    def getvalue(self):
        """
        Get all content.
        """
        content = ''.join(self._container)
        return content

    def isatty(self):
        """
        Used for the _install section: Redirected the syncdb command.
        It checks sys.stdout.isatty() in django.core.management.color
        """
        return False


