# coding: utf-8

"""
    PyLucid ToDo Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.utils.text import Truncator

from cms.utils.compat.dj import python_2_unicode_compatible
from cms.models import CMSPlugin

@python_2_unicode_compatible
class ToDoPlugin(CMSPlugin):
    code = models.TextField()

    def __str__(self):
        content = Truncator(strip_tags(self.code)).chars(30, html=True)
        return mark_safe(content)