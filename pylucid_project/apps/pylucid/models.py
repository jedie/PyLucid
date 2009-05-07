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
import sys
from xml.sax.saxutils import escape

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.db import transaction, IntegrityError
from django.http import HttpRequest

from pylucid.django_addons.comma_separated_field import CommaSeparatedCharField


def _get_request_from_args(args):
    """
    Helper function for getting the request object from the method arguments.
    Add a better traceback message if not requets object are in the method arguments.
    
    Used in UpdateInfoBaseModelManager().get_or_create() and UpdateInfoBaseModel().save()
    returns the request object and the args without the request object.
    """
    args = list(args) # convert tuple into list, so we can pop the first argument out.
         
    try:
        request = args.pop(0)
    except IndexError, err:
        # insert more information into the traceback
        etype, evalue, etb = sys.exc_info()
        # FIXME: How can we insert the original called method name?
        evalue = etype('Method needs request object as first argument!')
        raise etype, evalue, etb   
    
    assert isinstance(request, HttpRequest), \
        "First argument must be the request object! (It's type: %s)" % type(request)
    
    return request, args



class UpdateInfoBaseModelManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        """
        Same as django.db.models.query.QuerySet().get_or_create(), but here the first
        method argument must be the request object for passing it to the save() method.
        (For automatic update user ForeignKey in all UpdateInfoBaseModel's) 
        """
        assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
        
        # pop the request object from the arguments, insert a helpfull information in 
        # the traceback, if the request object is not the first argument
        request, args = _get_request_from_args(args)
        
        defaults = kwargs.pop('defaults', {})
        
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            try:
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                obj = self.model(**params)
                sid = transaction.savepoint()
                obj.save(request, force_insert=True)
                transaction.savepoint_commit(sid)
                return obj, True
            except IntegrityError, e:
                transaction.savepoint_rollback(sid)
                try:
                    return self.get(**kwargs), False
                except self.model.DoesNotExist:
                    raise e


class UpdateInfoBaseModel(models.Model):
    """
    Base model with update info attributes, used by many models.
    The createby and lastupdateby ForeignKey would be automaticly updated. This needs the 
    request object as the first argument in the save method.
    
    Important: Every own objects manager should be inherit from UpdateInfoBaseModelManager!
    """
    objects = UpdateInfoBaseModelManager()
    
    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        help_text="User as last edit the current page.",)
    
    def save(self, *args, **kwargs):
        """
        Automatic update createby and lastupdateby attributes with the request object witch must be
        the first argument.
        """
        # pop the request object from the arguments, insert a helpfull information in 
        # the traceback, if the request object is not the first argument:
        request, args = _get_request_from_args(args)
        
        try:
            current_user = request.user
        except AttributeError, err:
            # insert more information into the traceback
            etype, evalue, etb = sys.exc_info()
            # FIXME: How can we insert the original called method name?
            evalue = etype('request object has no user object!? (Original error: %s)' % err)
            raise etype, evalue, etb
                
        if self.pk == None: # New model entry
            self.createby = current_user
        self.lastupdateby = current_user
        return super(UpdateInfoBaseModel, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True




class PageTreeManager(UpdateInfoBaseModelManager):
    """
    Manager class for PageTree model
    
    inherited from UpdateInfoBaseModelManager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    def get_model_instance(self, request, ModelClass, pagetree=None):
        """
        Shared function for getting a model instance from the given model witch has
        a foreignkey to PageTree and Language model.
        Use the current language or the system default language.
        If pagetree==None: Use request.PYLUCID.pagetree
        """
        if not pagetree:
            # current pagetree instance from PyLucid objects
            pagetree = request.PYLUCID.pagetree
            
        queryset = ModelClass.objects.all().filter(page=pagetree)
        try:
            # Try to get the current used language
            return queryset.get(lang=request.PYLUCID.lang_entry)
        except ModelClass.DoesNotExist:
            # Get the PageContent entry in the system default language
            return queryset.get(lang=request.PYLUCID.default_lang_code)
    
    def get_pagemeta(self, request, pagetree=None):
        """
        Returns the pagemeta instance for pagetree and language.
        If there is no pagemate in the current language, use the system default language.
        If pagetree==None: Use request.PYLUCID.pagetree
        """
        return self.get_model_instance(request, PageMeta, pagetree)
    
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
                prefix_url = "/".join(path[:no+1])
                rest_url = "/".join(path[no+1:])
#                if not rest_url.endswith("/"):
#                    rest_url += "/"
                return (page, prefix_url, rest_url)

        return (page, None, None)

    def get_backlist(self, request, pagetree=None):
        """
        Generate a list of backlinks, usefull for generating a "You are here" breadcrumb navigation.
        TODO: filter showlinks and permit settings
        TODO: filter current site
        FIXME: Think this created many database requests
        """
        if pagetree == None:
            pagetree = request.PYLUCID.pagetree
        
        url = pagetree.get_absolute_url()
        
        pagemeta = self.get_pagemeta(request, pagetree)
        title = pagemeta.title_or_slug()
        
        backlist = [{"url": url, "title": title}]
        
        parent = pagetree.parent
        if parent: 
            # insert parent links
            backlist = self.get_backlist(request, parent) + backlist

        return backlist



class PageTree(UpdateInfoBaseModel):
    """
    The CMS page tree
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
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

    showlinks = models.BooleanField(default=True,
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )
    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group?",
        null=True, blank=True, 
    )
    permitEditGroup = models.ForeignKey(Group, related_name="%(class)s_permitEditGroup",
        help_text="Usergroup how can edit this page.",
        null=True, blank=True,
    )

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
        
        # FIXME: It would be great if we can order by get_absolute_url()
        ordering = ("id", "position")


#------------------------------------------------------------------------------


class Language(models.Model):
    code = models.CharField(unique=True, max_length=5)
    description = models.CharField(max_length=150, help_text="Description of the Language")

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group for a complete language section?",
        null=True, blank=True, 
    )

    def __unicode__(self):
        return u"Language %s - %s" % (self.code, self.description)

    class Meta:
        ordering = ("code",)


#------------------------------------------------------------------------------

class i18nPageTreeBaseModel(models.Model):
    """
    Base model for PageMeta, PluginPage and PageContent
    """
    page = models.ForeignKey(PageTree)
    lang = models.ForeignKey(Language)
    
    def get_absolute_url(self):
        """ Get the absolute url (without the domain/host part) """
        return self.page.get_absolute_url()
    
    class Meta:
        abstract = True



class PageMeta(i18nPageTreeBaseModel, UpdateInfoBaseModel):
    """
    Meta data for PageContent or PluginPage
    
    inherited attributes from i18nPageTreeBaseModel:
        page -> ForeignKey to PageTree
        lang -> ForeignKey to Language
        get_absolute_url()
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    title = models.CharField(blank=True, max_length=150, help_text="A long page title")
    keywords = CommaSeparatedCharField(blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group?",
        null=True, blank=True, 
    )

    def title_or_slug(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.title or self.page.slug

    def __unicode__(self):
        return u"PageMeta for page: '%s' (lang: '%s')" % (self.page.slug, self.lang.code)
    
    class Meta:
        unique_together = (("page","lang"),)
        ordering = ("page", "lang")

#------------------------------------------------------------------------------


class PluginPage(i18nPageTreeBaseModel, UpdateInfoBaseModel):
    """
    A plugin page
    
    inherited attributes from i18nPageTreeBaseModel:
        page -> ForeignKey to PageTree
        lang -> ForeignKey to Language
        get_absolute_url()
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    APP_LABEL_CHOICES = [(app,app) for app in settings.INSTALLED_APPS]
    
    pagemeta = models.ForeignKey(PageMeta)
    
    app_label = models.CharField(max_length=256, choices=APP_LABEL_CHOICES,
        help_text="The app lable witch is in settings.INSTALLED_APPS"
    )
    
    def title_or_slug(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.page.slug
    
    def get_plugin_name(self):
        return self.app_label.split(".")[-1]
    
    def save(self, *args, **kwargs):
        if not self.page.type == self.page.PLUGIN_TYPE:
            # FIXME: Better error with django model validation?
            raise AssertionError("Plugin can only exist on a plugin type tree entry!")
        return super(PluginPage, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u"PluginPage '%s' (page: %s)" % (self.app_label, self.page)
    
    class Meta:
        unique_together = (("page","lang"),)
        ordering = ("page", "lang")


#------------------------------------------------------------------------------


class PageContentManager(UpdateInfoBaseModelManager):
    """
    Manager class for PageContent model
    
    inherited from UpdateInfoBaseModelManager:
        get_or_create() method, witch expected a request object as the first argument.
    """    
    def get_sub_pages(self, pagecontent):
        """
        returns a list of all sub pages for the given PageContent instance
        TODO: filter showlinks and permit settings
        TODO: filter current site
        """
        current_lang = pagecontent.lang
        current_page = pagecontent.page
        sub_pages = PageContent.objects.all().filter(page__parent=current_page, lang=current_lang)
        return sub_pages   


class PageContent(i18nPageTreeBaseModel, UpdateInfoBaseModel):
    """
    A normal CMS Page with text content.

    inherited attributes from i18nPageTreeBaseModel:
        page -> ForeignKey to PageTree
        lang -> ForeignKey to Language
        get_absolute_url()

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
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
    
    objects = PageContentManager()

    pagemeta = models.ForeignKey(PageMeta)

    content = models.TextField(blank=True, help_text="The CMS page content.")
    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUP_CHOICES)

    def title_or_slug(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.page.slug

    def save(self, *args, **kwargs):
        if not self.page.type == self.page.PAGE_TYPE:
            # FIXME: Better error with django model validation?
            raise AssertionError("PageContent can only exist on a page type tree entry!")
        return super(PageContent, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PageContent '%s' (%s)" % (self.page.slug, self.lang)

    class Meta:
        unique_together = (("page","lang"),)
        ordering = ("page", "lang")


#------------------------------------------------------------------------------


class Design(UpdateInfoBaseModel):
    """
    Page design: template + CSS/JS files
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    name = models.CharField(unique=True, max_length=150, help_text="Name of this design combination",)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("EditableHtmlHeadFile", null=True, blank=True,
        help_text="Static files (stylesheet/javascript) for this page, included in html head via link tag"
    )

    def __unicode__(self):
        return u"Page design '%s'" % self.name
    
    class Meta:
        ordering = ("template",)


#------------------------------------------------------------------------------


class EditableHtmlHeadFile(UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry

    
    TODO: the save() method should be try to store the file into media path!
    """
    filename = models.CharField(unique=True, max_length=150)
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

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
        ordering = ("filename",)
