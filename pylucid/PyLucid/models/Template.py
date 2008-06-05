# -*- coding: utf-8 -*-
"""
    PyLucid.models.Template
    ~~~~~~~~~~~~~~~~~~~~~~~

    Model for Page Templates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    name = models.CharField(unique=True, max_length=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="template_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="template_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField()
    content = models.TextField()

    def save(self):
        """
        Delete the page cache if a template was edited.
        """
        from PyLucid.system.utils import delete_page_cache

        delete_page_cache()

        super(Template, self).save() # Call the "real" save() method

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)
        js = ['tiny_mce/tiny_mce.js', 'js/textareas_raw.js']

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'PyLucid_template'
        app_label = 'PyLucid'

