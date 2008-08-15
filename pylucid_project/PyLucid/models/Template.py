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
from django.contrib import admin
from django.contrib.auth.models import User

from PyLucid.tools.shortcuts import makeUnique
from PyLucid.system.utils import delete_page_cache


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
        if self.id == None:
            # Create a new template (e.g. used the save_as function)
            # http://www.djangoproject.com/documentation/admin/#save-as
            # The name must be unique.
            self.description += " (copy from %s)" % self.name
            existing_names = Template.objects.values_list("name", flat=True)
            # add a number if the name exist
            self.name = makeUnique(self.name, existing_names)

        delete_page_cache()

        super(Template, self).save() # Call the "real" save() method

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'PyLucid_template'
        app_label = 'PyLucid'


class TemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    list_display_links = ("name",)
    save_as = True


admin.site.register(Template, TemplateAdmin)