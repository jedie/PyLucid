# -*- coding: utf-8 -*-

"""
    SimpleStringIO
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django.conf import settings


class SimpleStringIO(object):
    """
    Minimalistic StringIO-file-like object.
    Encode unicode to the default charset (imported from the settings).
    See http://docs.python.org/lib/bltin-file-objects.html
    
    >>> s = SimpleStringIO()
    >>> s.write("one\\n")
    >>> s(u"two")
    >>> s.getvalue()
    'one\\ntwo'
    >>> s.getlines()
    ['one\n', 'two']
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

    def __call__(self, content):
        self.write(content)

    def getlines(self):
        """
        returns the container list
        """
        return self._container

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


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."