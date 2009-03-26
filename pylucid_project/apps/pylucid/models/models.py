#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

TYPE_CHOICES = (
            ('C', 'CMS-Page'),
            ('P', 'PluginPage'),
            )
MARKUPS = (
        (1,'plain'),
        (2,'html'),
        (3,'html+edit'),
        (4,'markdown'),
        (5,'wasweissich')
        )


class Page(models.Model):
    id = models.AutoField(primary_key=True)

    parent = models.ForeignKey("self", null=True,blank=True)
    position = models.IntegerField(default=0)
    slug = models.SlugField(unique=False)
    description = models.CharField(blank=True,max_length=150, help_text="For internal use")

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

#    template = models.ForeignKey("Template")
#    style = models.ForeignKey("Style")

    class Meta:
        unique_together =(("slug","parent"))
    
class Language(models.Model):
    code = models.CharField(unique=True,max_length=5)
    description = models.CharField(max_length=150,help_text="Description of the Language")

class PageContent(models.Model):
    page = models.ForeignKey(Page)
    lang = models.ForeignKey(Language)

    title = models.CharField(blank=True,max_length=150)
    content = models.TextField(blank = True)
    keywords = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

#    template = models.ForeinKey("Template")
#    style = models.ForeignKey("Style")

    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUPS)

    class Meta:
        unique_together = (("page","lang"))
