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

import os
from xml.sax.saxutils import escape

from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string

from pylucid.django_addons.comma_separated_field import CommaSeparatedCharField

class PageTreeManager(models.Manager):
    """ Manager class for PageTree model """
    def get_page_from_url(self, url_path):
        """ returns a tuple the page tree instance from the given url_path"""
        path = url_path.split("/")
        page = None
        for no, page_slug in enumerate(path):
            try:
                page = PageTree.objects.get(parent=page, slug=page_slug)
            except PageTree.DoesNotExist:
                raise PageTree.DoesNotExist("Wrong url part: %s" % escape(page_slug))

            if page.type == PageTree.PLUGIN_TYPE:
                # It's a plugin
                rest_url = "/".join(path[no+1:])
                return (page, rest_url)

        return (page, "")


class PageTree(models.Model):
    """ The CMS page tree """
    PAGE_TYPE = 'C'
    PLUGIN_TYPE = 'P'

    TYPE_CHOICES = (
        (PAGE_TYPE, 'CMS-Page'),
        (PLUGIN_TYPE , 'PluginPage'),
    )
    TYPE_DICT = dict(TYPE_CHOICES)

    objects = PageTreeManager()

    id = models.AutoField(primary_key=True)

    site = models.ForeignKey(Site, verbose_name=_('Site'))

    parent = models.ForeignKey("self", null=True, blank=True, help_text="the higher-ranking father page")
    position = models.SmallIntegerField(default=0,
        help_text="ordering weight for sorting the pages in the menu.")
    slug = models.SlugField(unique=False, help_text="(for building URLs)")
    description = models.CharField(blank=True, max_length=150, help_text="For internal use")

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    design = models.ForeignKey("Design", help_text="Page Template, CSS/JS files")

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
    createby = models.ForeignKey(User, editable=True, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey(User, editable=True, related_name="%(class)s_lastupdateby",
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
        unique_together=(("slug","parent"),)
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


class PageContentManager(models.Manager):
    """ Manager class for PageContent model """
    def get_backlist(self, pagecontent):
        """
        returns a list of PageContent instance objects back to the tree root.
        Usefull for generating a "You are here" breadcrumb navigation
        TODO: filter showlinks and permit settings
        """
        parent = pagecontent.page.parent          
        if parent:
            lang = pagecontent.lang
            parent_content = self.get(page=parent, lang=lang)
            backlist = self.get_backlist(parent_content)
            backlist.append(pagecontent)
            return backlist
        else:
            return [pagecontent]
    
    def get_sub_pages(self, pagecontent):
        """
        returns a list of all sub pages for the given PageContent instance
        TODO: filter showlinks and permit settings
        """
        current_lang = pagecontent.lang
        current_page = pagecontent.page
        sub_pages = PageContent.objects.all().filter(page__parent=current_page, lang=current_lang)
        return sub_pages   


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
    
    objects = PageContentManager()

    page = models.ForeignKey(PageTree)
    lang = models.ForeignKey(Language)

    title = models.CharField(blank=True, max_length=150, help_text="A long page title")
    content = models.TextField(blank=True, help_text="The CMS page content.")
    keywords = CommaSeparatedCharField(blank=True, max_length=255,
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
    createby = models.ForeignKey( User, editable=True, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey( User, editable=True, related_name="%(class)s_lastupdateby",
        help_text="User as last edit the current page.",)

    def title_or_slug(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        if self.title:
            return self.title
        return self.page.slug

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        return "/" + self.lang.code + self.page.get_absolute_url()

    def __unicode__(self):
        return u"PageContent '%s' (%s)" % (self.page.slug, self.lang)

    class Meta:
        unique_together = (("page","lang"),)
        db_table = 'PyLucid_PageContent'
#        app_label = 'PyLucid'



class Design(models.Model):
    """
    Page design: template + CSS/JS files
    """
    name = models.CharField(unique=True, max_length=150, help_text="Name of this design combination",)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("EditableHtmlHeadFile", null=True, blank=True,
        help_text="Static files (stylesheet/javascript) for this page, included in html head via link tag")

    def __unicode__(self):
        return u"Page design '%s'" % self.name


class EditableHtmlHeadFile(models.Model):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.
    
    TODO: the save() method should be try to store the file into media path!
    """
    filename = models.CharField(unique=True, max_length=150)
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User, related_name="%(class)s_createby", null=True, blank=True)
    lastupdateby = models.ForeignKey(User, related_name="%(class)s_lastupdateby", null=True, blank=True)

    def get_mimetype(self):
        if self.filename.endswith(".css"):
            return u"text/css"
        elif self.filename.endswith(".js"):
            return u"text/javascript"
        else:
            from mimetypes import guess_type
            returnguess_type(self.filename)[0] or u"application/octet-stream"            

    def get_head_template(self):
        """ returns the template name for building the html head link. """
        ext = os.path.splitext(self.filename)[1].strip(".")
        return settings.PYLUCID.EDITABLE_HEAD_LINK_TEMPLATE % ext

    def get_head_link(self):
        """
        TODO: Should check if the file was saved into media path
        """
        template_name = self.get_head_template()
        filename = self.filename
        url = reverse("PyLucid-send_head_file", kwargs={"filename": filename})
        head_link = render_to_string(template_name, {'url': url})
        return head_link

    def __unicode__(self):
        return u"EditableHtmlHeadFile '%s'" % self.filename

    class Meta:
        db_table = 'PyLucid_EditableStaticFile'
