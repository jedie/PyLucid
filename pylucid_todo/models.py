# coding: utf-8

"""
    PyLucid ToDo Plugin
    ~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from cms.models import CMSPlugin

class ToDoPlugin(CMSPlugin):
    code = models.TextField()
