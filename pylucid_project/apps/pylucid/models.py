# coding: utf-8

"""
    PyLucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    New PyLucid models since v0.9
    
    TODO:
        Where to store bools like: showlinks, permitViewPublic ?

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
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from dbtemplates.models import Template

class PageTree(models.Model):
    """ The CMS page tree """
    PAGE_TYPE = 'C'
    PLUGIN_TYPE = 'P'

    TYPE_CHOICES = (
        (PAGE_TYPE, 'CMS-Page'),
        (PLUGIN_TYPE , 'PluginPage'),
    )
    TYPE_DICT = dict(TYPE_CHOICES)

    id = models.AutoField(primary_key=True)

    site = models.ForeignKey(Site, verbose_name=_('Site'))

    parent = models.ForeignKey("self", null=True, blank=True, help_text="the higher-ranking father page")
    position = models.SmallIntegerField(default=0,
        help_text="ordering weight for sorting the pages in the menu.")
    slug = models.SlugField(unique=False, help_text="(for building URLs)")
    description = models.CharField(blank=True, max_length=150, help_text="For internal use")

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    template = models.ForeignKey(Template, to_field="id", help_text="the used template for this page")
#    style = models.ForeignKey(Style, to_field="id", help_text="the used stylesheet for this page")
    staticfiles = models.ManyToManyField("EditableStaticFile",
        help_text="Static files (stylesheet/javascript) for this page, included in html head via link tag")

#    showlinks = models.BooleanField(default=True,
#        help_text="Put the Link to this page into Menu/Sitemap etc.?")
#    permitViewPublic = models.BooleanField(default=True,
#        help_text="Can anonymous see this page?")
#    permitViewGroup = models.ForeignKey(Group, related_name="page_permitViewGroup", null=True, blank=True,
#        help_text="Limit viewable to a group?")
#    permitEditGroup = models.ForeignKey(Group, related_name="page_permitEditGroup", null=True, blank=True,
#        help_text="Usergroup how can edit this page.")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        help_text="User as last edit the current page.",)       

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            return parent_shortcut + self.slug + "/"
        else:
            return "/" + self.slug + "/"

    def __unicode__(self):
        return u"PageTree '%s' (type: %s)" % (self.slug, self.TYPE_DICT[self.type])

    class Meta:
        unique_together =(("slug","parent"))
        db_table = 'PyLucid_PageTree'
#        app_label = 'PyLucid'


class Language(models.Model):
    code = models.CharField(unique=True, max_length=5)
    description = models.CharField(max_length=150, help_text="Description of the Language")

    def __unicode__(self):
        return u"Language %s - %s" % (self.code, self.description)

    class Meta:
        db_table = 'PyLucid_Language'
#        app_label = 'PyLucid'


class PageContent(models.Model):
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
    
    page = models.ForeignKey(PageTree)
    lang = models.ForeignKey(Language)

    title = models.CharField(blank=True, max_length=150, help_text="A long page title")
    content = models.TextField(blank=True, help_text="The CMS page content.")
    keywords = models.CharField(blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)")
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUP_CHOICES)

#    showlinks = models.BooleanField(default=True,
#        help_text="Put the Link to this page into Menu/Sitemap etc.?")
#    permitViewPublic = models.BooleanField(default=True,
#        help_text="Can anonymous see this page?")
#    permitViewGroup = models.ForeignKey(Group, related_name="page_permitViewGroup", null=True, blank=True,
#        help_text="Limit viewable to a group?")
#    permitEditGroup = models.ForeignKey(Group, related_name="page_permitEditGroup", null=True, blank=True,
#        help_text="Usergroup how can edit this page.")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey( User, editable=False, related_name="%(class)s_lastupdateby",
        help_text="User as last edit the current page.",)

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        return "/" + self.lang.code + self.page.get_absolute_url()

    def __unicode__(self):
        return u"PageContent '%s' (%s)" % (self.page.slug, self.lang)

    class Meta:
        unique_together = (("page","lang"))
        db_table = 'PyLucid_PageContent'
#        app_label = 'PyLucid'





class EditableStaticFile(models.Model):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.
    """
    name = models.CharField(unique=True, max_length=150)
    description = models.TextField(null=True, blank=True)
    content = models.TextField()
    
    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User, related_name="%(class)s_createby", null=True, blank=True)
    lastupdateby = models.ForeignKey(User, related_name="%(class)s_lastupdateby", null=True, blank=True)

    def __unicode__(self):
        return u"EditableStaticFile %r" % self.name

    class Meta:
        db_table = 'PyLucid_EditableStaticFile'
