# -*- coding: utf-8 -*-
"""
    PyLucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    Old PyLucid v0.8 models, used for migrating data into the new v0.9 models.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-02-20 09:22:34 +0100 (Fr, 20 Feb 2009) $
    $Rev: 1831 $
    $Author: JensDiemer $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group


class PageManager(models.Manager):
    """
    Manager for Page model.
    """
    pass

#______________________________________________________________________________

class Page08(models.Model):
    """
    A CMS Page Object

    TODO: We should refactor the "pre_save" behavior, use signals:
    http://code.djangoproject.com/wiki/Signals
    """

    # IDs used in other parts of PyLucid, too
    MARKUP_CREOLE       = 6
    MARKUP_HTML         = 0
    MARKUP_HTML_EDITOR  = 1
    MARKUP_TINYTEXTILE  = 2
    MARKUP_TEXTILE      = 3
    MARKUP_MARKDOWN     = 4
    MARKUP_REST         = 5

    MARKUP_CHOICES = (
        (MARKUP_CREOLE      , u'Creole wiki markup'),
        (MARKUP_HTML        , u'html'),
        (MARKUP_HTML_EDITOR , u'html + JS-Editor'),
        (MARKUP_TINYTEXTILE , u'textile'),
        (MARKUP_TEXTILE     , u'Textile (original)'),
        (MARKUP_MARKDOWN    , u'Markdown'),
        (MARKUP_REST        , u'ReStructuredText'),
    )
    MARKUP_DICT = dict(MARKUP_CHOICES)
    #--------------------------------------------------------------------------

    objects = PageManager()

    # Explicite id field, so we can insert a help_text ;)
    id = models.AutoField(primary_key=True, help_text="The internal page ID.")

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "self", null=True, blank=True,
        to_field="id", help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default = 0,
        help_text = "ordering weight for sorting the pages in the menu."
    )

    name = models.CharField(
        blank=False, null=False,
        max_length=150, help_text="A short page name"
    )

    shortcut = models.CharField(
        unique=True, null=False, blank=False,
        max_length=150, help_text="shortcut to built the URLs",

    )
    title = models.CharField(
        blank=True, max_length=150, help_text="A long page title"
    )

    template = models.ForeignKey(
        "Template", to_field="id", help_text="the used template for this page"
    )
    style = models.ForeignKey(
        "Style", to_field="id", help_text="the used stylesheet for this page"
    )
    markup = models.IntegerField(
        db_column="markup_id", # Use the old column name.
        max_length=1, choices=MARKUP_CHOICES,
        help_text="the used markup language for this page",
    )

    keywords = models.CharField(
        blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(
        blank=True, max_length=255,
        help_text="Short description of the contents. (for the html header)"
    )

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False, related_name="page_createby",
        help_text="User how create the current page.",
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, related_name="page_lastupdateby",
        help_text="User as last edit the current page.",
    )

    showlinks = models.BooleanField(default=True,
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )
    permitViewPublic = models.BooleanField(default=True,
        help_text="Can anonymous see this page?"
    )

    permitViewGroup = models.ForeignKey(
        Group, related_name="page_permitViewGroup", null=True, blank=True,
        help_text="Limit viewable to a group?"
    )

    permitEditGroup = models.ForeignKey(
        Group, related_name="page_permitEditGroup", null=True, blank=True,
        help_text="Usergroup how can edit this page."
    )

    class Meta:
        db_table = 'PyLucid_page'
        app_label = 'PyLucid'

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        parent_shortcut = ""
        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            return parent_shortcut + self.shortcut + "/"
        else:
            return "/" + self.shortcut + "/"

    def __unicode__(self):
        return u"old page model %r" % self.shortcut



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

    def __unicode__(self):
        return u"old page template %r" % self.name

    class Meta:
        db_table = 'PyLucid_template'
        app_label = 'PyLucid'




class Style(models.Model):
    name = models.CharField(unique=True, max_length=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="style_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="style_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def __unicode__(self):
        return u"old page stylesheet %r" % self.name

    class Meta:
        db_table = 'PyLucid_style'
        app_label = 'PyLucid'
