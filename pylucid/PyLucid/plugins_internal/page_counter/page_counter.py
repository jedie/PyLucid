# -*- coding: utf-8 -*-

"""
    Counter
    ~~~~~~~

    Simple page counter.
    Note: Counts not cached views!

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

from django.db import models

from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin

#_____________________________________________________________________________
# models

class PageCount(models.Model):
    page = models.ForeignKey(Page)
    counter = models.PositiveIntegerField()

    class Meta:
        app_label = 'PyLucidPlugins' # essential

# essential: a list of all plugin models:
PLUGIN_MODELS = (PageCount,)


class page_counter(PyLucidBasePlugin):

    def lucidTag(self, **kwargs):
        """
        increase the page count and display the current count number.
        """
        try:
            # Get or create the page counter for the current page
            page_count, created = PageCount.objects.get_or_create(
                page = self.current_page, # PyLucid.models.Page instance
                defaults = {"counter": 1}
            )
        except Exception, err:
            self.page_msg.red("Page counter error: %s" % err)
            return

        if not created:
            # increase a existing page count entry
            page_count.counter += 1
            page_count.save()

        # Display the current page count number
        self.response.write("%i" % page_count.counter)
