# -*- coding: utf-8 -*-

"""
    PyLucid permalink
    ~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


__version__= "$Rev: $"


from django.conf import settings

from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin




class permalink(PyLucidBasePlugin):

    def lucidTag(self, id=None, shortcut=""):
        """
        Create a html link with absolute path to the page, based on the page id.
        The shortcut argument is only for a nicer lucidTag!
        """
        context = {
            # Only for fallback:
            "id": id,
            "shortcut": shortcut,
            "prefix": settings.PERMALINK_URL_PREFIX,
        }
        if not id:
            if self.request.debug:
                msg = "Error: No 'id' argument in lucidTag permalink!"
                self.page_msg(msg)
                context["msg"] = msg
        else:
            try:
                context["page"] = Page.objects.get(id=id)
            except Page.DoesNotExist, err:
                if self.request.debug:
                    msg = "Wrong id '%s' in lucidTag permalink: %s" % (id, err)
                    self.page_msg.red(msg)
                    context["msg"] = msg
            
        self._render_template("html_permalink", context, debug=True)
