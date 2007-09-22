#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A minimalistic StringIO-file-like object.

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


#if __name__ == "__main__": # A local test. THIS SHOULD BE COMMENTED!!!
#    import os
#    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
#    from django.conf import settings
#    from django.core import management
#    management.setup_environ(settings) # init django


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

#if __name__ == "__main__":
#     A local test: You must uncomment the django local init part above!
#    response = SimpleStringIO()
#    response.write(u"test")
#    response.write("\n")
#    response.write("test")
#    print response.getvalue()