# -*- coding: utf-8 -*-

"""
    PyLucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    New PyLucid models since v0.9

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group


class PageTree(models.Model):
    """ The CMS page tree """
    TYPE_CHOICES = (
        ('C', 'CMS-Page'),
        ('P', 'PluginPage'),
    )

    id = models.AutoField(primary_key=True)

    parent = models.ForeignKey("self", null=True, blank=True, help_text="the higher-ranking father page")
    position = models.SmallIntegerField(default=0,
        help_text="ordering weight for sorting the pages in the menu.")
    slug = models.SlugField(unique=False, help_text="(for building URLs)")
    description = models.CharField(blank=True, max_length=150, help_text="For internal use")

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

#    template = models.ForeignKey("Template")
#    style = models.ForeignKey("Style")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="page_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey( User, editable=False, related_name="page_lastupdateby",
        help_text="User as last edit the current page.",)

    class Meta:
        unique_together =(("slug","parent"))


class Language(models.Model):
    code = models.CharField(unique=True, max_length=5)
    description = models.CharField(max_length=150, help_text="Description of the Language")


class PageContent(models.Model):
    MARKUPS = (
        (1,'plain'),
        (2,'html'),
        (3,'html+edit'),
        (4,'markdown'),
        (5,'wasweissich'),
    )
    page = models.ForeignKey(PageTree)
    lang = models.ForeignKey(Language)

    title = models.CharField(blank=True, max_length=150, help_text="A long page title")
    content = models.TextField(blank=True, help_text="The CMS page content.")
    keywords = models.CharField(blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)")
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

#    template = models.ForeinKey("Template")
#    style = models.ForeignKey("Style")

    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUPS)

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="page_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey( User, editable=False, related_name="page_lastupdateby",
        help_text="User as last edit the current page.",)

    class Meta:
        unique_together = (("page","lang"))
