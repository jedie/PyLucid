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
import errno
import warnings
import posixpath
import mimetypes
from xml.sax.saxutils import escape

from django.db import models
from django.conf import settings
from django.core import exceptions
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.auth.models import User, Group, Permission

# http://code.google.com/p/django-tagging/
import tagging
from tagging.fields import TagField

# http://code.google.com/p/django-tools/
from django_tools.utils import installed_apps_utils
from django_tools.middlewares import ThreadLocal
from django_tools.template import render
from django_tools import model_utils

from pylucid_project.utils import crypt, form_utils
from pylucid_project.system.pylucid_plugins import PYLUCID_PLUGINS

from pylucid.system.auto_model_info import UpdateInfoBaseModel, AutoSiteM2M
from pylucid.tree_model import BaseTreeModel, TreeManager, TreeGenerator
from pylucid.shortcuts import failsafe_message
from pylucid.system import pylucid_objects
from pylucid.fields import ColorValueField
from pylucid.system import headfile

from pylucid_plugins import page_update_list


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class BaseModel(models.Model):
    def get_absolute_url(self):
        raise NotImplementedError
    get_absolute_url.short_description = _('absolute url')

    def get_site(self):
        raise NotImplementedError
    get_site.short_description = _('on site')

    def get_absolute_uri(self):
        """ returned the complete absolute URI (with the domain/host part) """
        request = ThreadLocal.get_current_request()
        is_secure = request.is_secure()
        if is_secure:
            protocol = "https://"
        else:
            protocol = "http://"
        site = self.get_site()
        domain = site.domain
        absolute_url = self.get_absolute_url()
        return protocol + domain + absolute_url
    get_absolute_uri.short_description = _('absolute uri')

    class Meta:
        abstract = True



class BaseModelManager(models.Manager):
    def easy_create(self, cleaned_form_data, extra={}):
        """
        Creating a new model instance with cleaned form data witch can hold more data than for
        this model needed.
        """
        keys = self.model._meta.get_all_field_names()
        model_kwargs = form_utils.make_kwargs(cleaned_form_data, keys)
        model_kwargs.update(extra)
        model_instance = self.model(**model_kwargs)
        model_instance.save()
        return model_instance



class PageTreeManager(BaseModelManager):
    """
    Manager class for PageTree model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    def filter_accessible(self, queryset, user):
        """ filter all pages with can't accessible for the given user """

        if user.is_anonymous():
            # Anonymous user are in no user group
            return queryset.filter(permitViewGroup__isnull=True)

        if user.is_superuser:
            # Superuser can see everything ;)
            return queryset

        # filter pages for not superuser and not anonymous

        user_groups = user.groups.values_list('pk', flat=True)

        if not user_groups:
            # User is in no group
            return queryset.filter(permitViewGroup__isnull=True)

        # Filter out all view group
        return queryset.filter(
            models.Q(permitViewGroup__isnull=True) | models.Q(permitViewGroup__in=user_groups)
        )

    def all_accessible(self, user):
        """ returns all pages that the given user can access. """
        queryset = self.model.on_site
        queryset = self.filter_accessible(queryset, user)
        return queryset

    def get_tree(self, user, filter_showlinks=False):
        """ return a TreeGenerator instance with all accessable page tree instance """
        queryset = self.all_accessible(user)

        if filter_showlinks:
            # Filter PageTree.showlinks
            queryset = queryset.filter(showlinks=True)

        queryset = queryset.order_by("position")
        tree = TreeGenerator(queryset, skip_no_parent=True)

        return tree

#    def easy_create(self, cleaned_form_data, page_type):
#        """
#        Creating a new PageTree entry with cleaned form data witch can hold more data than for
#        this model
#        """
#        pagetree_kwargs = form_utils.make_kwargs(
#            cleaned_form_data, keys=PageTree._meta.get_all_field_names()
#        )
#        assert page_type in PageTree.TYPE_DICT
#        pagetree_kwargs["type"] = page_type
#
#        pagetree_instance = PageTree(**pagetree_kwargs)
#        pagetree_instance.save()
#        return pagetree_instance

    def get_root_page(self, user, filter_parent=True):
        """ returns the 'first' root page tree entry witch the user can access """
        queryset = self.all_accessible(user)

        if filter_parent:
            # All "root" pages
            queryset = queryset.filter(parent=None).order_by("position")
        else:
            # fallback if no "root" page is accessable
            queryset = queryset.order_by("parent", "position")

        try:
            return queryset[0]
        except IndexError, err:
            if self.model.on_site.count() == 0:
                raise PageTree.DoesNotExist("There exist no PageTree items! Have you install PyLucid?")
            elif filter_parent == True:
                # If all root pages not accessible for the current user
                # -> try to get the first accessable page
                return self.get_root_page(user, filter_parent=False)
            else:
                raise

    def get_model_instance(self, request, ModelClass, pagetree=None, show_lang_info=True):
        """
        Shared function for getting a model instance from the given model witch has
        a foreignkey to PageTree and Language model.
        Use the current language or the system default language.
        If pagetree==None: Use request.PYLUCID.pagetree
        If show_lang_info: Create a page_msg if requested item doesn't exist in client favored language.
        """
        # client favored Language instance:
        lang_entry = request.PYLUCID.lang_entry
        # default Language instance set in system preferences:
        default_lang_entry = request.PYLUCID.default_lang_entry

        lang_entry = request.PYLUCID.lang_entry
        default_lang_entry = request.PYLUCID.default_lang_entry

        if not pagetree:
            # current pagetree instance
            pagetree = request.PYLUCID.pagetree

        queryset = ModelClass.objects.all().filter(page=pagetree)
        try:
            # Try to get the current used language
            return queryset.get(lang=lang_entry)
        except ModelClass.DoesNotExist:
            # Get the PageContent entry in the system default language
            try:
                instance = queryset.get(lang=default_lang_entry)
            except ModelClass.DoesNotExist, err:
                msg = (
                    "%r doesn't exist for %r in client favored language %r"
                    " and not in system default language %r!"
                    " Original Error was: %s"
                ) % (ModelClass, pagetree, lang_entry, default_lang_entry, err)
                raise ModelClass.DoesNotExist(msg)

            if show_lang_info and (settings.DEBUG or settings.PYLUCID.I18N_DEBUG):
                request.page_msg.error(
                    "Page '%s' doesn't exist in client favored language '%s', use '%s' entry." % (
                        pagetree.slug, lang_entry.code, instance.lang.code
                    )
                )
            return instance


    def get_pagemeta(self, request, pagetree=None, show_lang_info=False):
        """
        Returns the PageMeta instance for pagetree and language.
        If there is no PageMeta in the current language, use the system default language.
        If pagetree==None: Use request.PYLUCID.pagetree
        """
        return self.get_model_instance(request, PageMeta, pagetree, show_lang_info)

    def get_pagecontent(self, request, pagetree=None, show_lang_info=False):
        """
        Returns the PageContent instance for pagetree and language.
        If there is no PageContent in the current language, use the system default language.
        If pagetree==None: Use request.PYLUCID.pagetree
        """
        pagemeta = self.get_model_instance(request, PageMeta, pagetree, show_lang_info)
        pagecontent = PageContent.objects.get(pagemeta=pagemeta)
        return pagecontent

    def get_page_from_url(self, request, url_path):
        """
        returns a tuple the page tree instance from the given url_path
        XXX: move it out from model?
        """
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()

        path = url_path.split("/")
        page = None
        for no, page_slug in enumerate(path):
            try:
                page = PageTree.on_site.get(parent=page, slug=page_slug)
            except PageTree.DoesNotExist:
                raise PageTree.DoesNotExist("Wrong url part: %s" % escape(page_slug))

            page_view_group = page.permitViewGroup

            # Check permissions
            if request.user.is_anonymous():
                # Anonymous user are in no user group
                if page_view_group != None:
                    # XXX: raise permission deny?
                    msg = "Permission deny"
                    if settings.DEBUG:
                        msg += " (url part: %s)" % escape(page_slug)
                    raise PageTree.DoesNotExist(msg)
            elif not request.user.is_superuser: # Superuser can see everything ;)
                if (page_view_group != None) and (page_view_group not in user_groups):
                    msg = "Permission deny"
                    if settings.DEBUG:
                        msg += " (not in view group %r, url part: %r)" % (page_view_group, escape(page_slug))
                    raise PageTree.DoesNotExist(msg)

            if page.page_type == PageTree.PLUGIN_TYPE:
                # It's a plugin
                prefix_url = "/".join(path[:no + 1])
                rest_url = "/".join(path[no + 1:])
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

        pagemeta = self.get_pagemeta(request, pagetree)
        url = pagemeta.get_absolute_url()
        page_name = pagemeta.get_name()
        page_title = pagemeta.get_title()

        backlist = [{"url": url, "name": page_name, "title": page_title}]

        parent = pagetree.parent
        if parent:
            # insert parent links
            backlist = self.get_backlist(request, parent) + backlist

        return backlist


class PageTree(BaseModel, BaseTreeModel, UpdateInfoBaseModel):
    """
    The CMS page tree

    inherited attributes from TreeBaseModel:
        parent
        position

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

    slug = models.SlugField(unique=False, help_text="(for building URLs)")

    site = models.ForeignKey(Site, default=Site.objects.get_current)
    on_site = CurrentSiteManager()

    page_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    design = models.ForeignKey("Design", help_text="Page Template, CSS/JS files")

    showlinks = models.BooleanField(default=True,
        help_text="Accessable for all users, but don't put a Link to this page into menu/sitemap etc."
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
        """ absolute url *without* language code (without domain/host part) """
        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            return parent_shortcut + self.slug + "/"
        else:
            return "/" + self.slug + "/"

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.site

    def __unicode__(self):
        return u"PageTree '%s' (id: %r, site: %r, type: %r)" % (
            self.slug, self.id, self.site.name, self.TYPE_DICT.get(self.page_type)
        )

    class Meta:
        verbose_name_plural = verbose_name = "PageTree"
        unique_together = (("site", "slug", "parent"),)

        # FIXME: It would be great if we can order by get_absolute_url()
#        ordering = ("site", "id", "position")
        ordering = ("-lastupdatetime",)

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageTree)


#------------------------------------------------------------------------------

class LanguageManager(models.Manager):
    def get_choices(self):
        """ return a tuple list for e.g. forms.ChoiceField """
        return self.values_list('code', 'description')

    def get_default_lang_entry(self,):
        """ returns default Language instance, setup in system preferences. """
        from pylucid.preference_forms import SystemPreferencesForm # FIXME: import here, against import loop.
        system_preferences = SystemPreferencesForm().get_preferences()
        default_lang_code = system_preferences["lang_code"]
        default_lang_entry, created = self.get_or_create(code=default_lang_code)
        if created:
            failsafe_message("Default system language %r created!" % default_lang_entry)
        return default_lang_entry

    def get_current_lang_entry(self, request=None):
        """ return client Language instance, if not available, use get_default_lang_entry() """
        if request == None:
            request = ThreadLocal.get_current_request()

        if request:
            if hasattr(request, "PYLUCID"):
                return request.PYLUCID.lang_entry

            if hasattr(request, "LANGUAGE_CODE"):
                lang_code = request.LANGUAGE_CODE
                if "-" in lang_code:
                    lang_code = lang_code.split("-", 1)[0]
                try:
                    return self.get(code=lang_code)
                except Language.DoesNotExist:
                    if settings.PYLUCID.I18N_DEBUG:
                        msg = (
                            'Favored language "%s" does not exist -> use default lang from system preferences'
                        ) % request.LANGUAGE_CODE
                        failsafe_message(msg)

        return self.get_default_lang_entry()


class Language(models.Model):
    objects = LanguageManager()

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

class PageMeta(BaseModel, UpdateInfoBaseModel):
    """
    Meta data for PageContent or PluginPage

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = BaseModelManager()

    page = models.ForeignKey(PageTree)
    lang = models.ForeignKey(Language)

    name = models.CharField(blank=True, max_length=150,
        help_text="Sort page name (for link text in e.g. menu)"
    )
    title = models.CharField(blank=True, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )

    tags = TagField(# from django-tagging
        help_text=mark_safe(
            _('tags for this entry. <a href="%s" class="openinwindow"'
            ' title="Information about tag splitting.">tag format help</a>') % TAG_INPUT_HELP_URL
        )
    )

    keywords = models.CharField(blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

    robots = models.CharField(blank=True, max_length=255, default="index,follow",
        help_text="for html 'robots' meta content."
    )

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group?",
        null=True, blank=True,
    )

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.lang.code
        page_url = self.page.get_absolute_url()
        return "/" + lang_code + page_url

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.page.site
    get_site.short_description = _('on site')
    get_site.allow_tags = False

    def get_other_languages(self):
        return PageMeta.objects.all().filter(page=self.page).exclude(lang=self.lang)

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.title or self.get_name()

    def get_name(self):
        return self.name or self.page.slug

    def __unicode__(self):
        return u"PageMeta for page: '%s' (lang: '%s')" % (self.page.slug, self.lang.code)

    class Meta:
        verbose_name_plural = verbose_name = "PageMeta"
        unique_together = (("page", "lang"),)
        ordering = ("-lastupdatetime",)
#        ordering = ("page", "lang")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageMeta)

#------------------------------------------------------------------------------

class RootAppChoiceField(models.CharField):
    def get_choices_default(self):
        PluginPage.objects.get_app_choices()

class PluginPageManager(BaseModelManager):
    _APP_CHOICES = None
    def get_app_choices(self):
        if self._APP_CHOICES == None:
            root_apps = installed_apps_utils.get_filtered_apps(resolve_url="/")
            self._APP_CHOICES = [("", "---------")] + [(app, app) for app in root_apps]
        return self._APP_CHOICES

    def reverse(self, plugin_name, viewname, args=(), kwargs={}):
        """
        reverse a plugin url.
        Please note: this will always use the first PluginPage entry as url prefix!
        """
        # get the app label from
        plugin_instance = PYLUCID_PLUGINS["blog"]
        app_label = plugin_instance.pkg_string

        # Get the first PluginPage entry for this plugin
        queryset = PluginPage.objects.all()
        queryset = queryset.filter(pagemeta__page__site=Site.objects.get_current())
        queryset = queryset.filter(app_label=app_label)
        plugin_page = queryset[0]

        url_prefix = plugin_page.get_absolute_url()
        plugin_url_resolver = plugin_instance.get_plugin_url_resolver(url_prefix, plugin_page.urls_filename)
        return plugin_url_resolver.reverse(viewname, *args, **kwargs)


class PluginPage(BaseModel, UpdateInfoBaseModel):
    """
    A plugin page

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = PluginPageManager()

    pagemeta = models.ManyToManyField(PageMeta)

    app_label = RootAppChoiceField(max_length=256,
        help_text=(
            "The plugin app label witch is in settings.INSTALLED_APPS"
            " (Only apps witch can handle a root url.)"
        )
    )
    urls_filename = models.CharField(max_length=256, default="urls.py",
        help_text="Filename of the urls.py"
    )

    def get_pagemeta(self):
        lang_entry = Language.objects.get_current_lang_entry()
        try:
            return self.pagemeta.get(lang=lang_entry)
        except PageMeta.DoesNotExist:
            default_lang_entry = Language.objects.get_default_lang_entry()
            return self.pagemeta.get(lang=default_lang_entry)

    def get_site(self):
        pagemeta = self.get_pagemeta()
        return pagemeta.page.site

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        pagemeta = self.get_pagemeta()
        return pagemeta.get_absolute_url()

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        pagemeta = self.get_pagemeta()
        return pagemeta.get_title()

    def get_plugin_name(self):
        return self.app_label.split(".")[-1]

    def get_plugin(self):
        """ returns pylucid_project.system.pylucid_plugins instance """
        plugin_name = self.get_plugin_name()
        plugin_instance = PYLUCID_PLUGINS[plugin_name]
        return plugin_instance

    def save(self, *args, **kwargs):
#        if not self.page.page_type == self.page.PLUGIN_TYPE:
#            # FIXME: Better error with django model validation?
#            raise AssertionError("Plugin can only exist on a plugin type tree entry!")
        return super(PluginPage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PluginPage '%s' (%s)" % (self.app_label, self.get_absolute_url())

    class Meta:
        verbose_name_plural = verbose_name = "PluginPage"
        ordering = ("-lastupdatetime",)
#        ordering = ("page", "lang")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PluginPage)

#------------------------------------------------------------------------------


class PageContentManager(BaseModelManager):
    """
    Manager class for PageContent model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    pass


class PageContent(BaseModel, UpdateInfoBaseModel):
    """
    A normal CMS Page with text content.

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    # IDs used in other parts of PyLucid, too
    MARKUP_CREOLE = 6
    MARKUP_HTML = 0
    MARKUP_HTML_EDITOR = 1
    MARKUP_TINYTEXTILE = 2
    MARKUP_TEXTILE = 3
    MARKUP_MARKDOWN = 4
    MARKUP_REST = 5

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

    pagemeta = models.OneToOneField(PageMeta)

    content = models.TextField(blank=True, help_text="The CMS page content.")
    markup = models.IntegerField(db_column="markup_id", max_length=1, choices=MARKUP_CHOICES)

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.pagemeta.lang.code
        page_url = self.pagemeta.page.get_absolute_url()
        return "/" + lang_code + page_url

    def get_site(self):
        return self.pagemeta.page.site

    def get_update_info(self):
        """ update info for page_update_list.models.UpdateJournal used by page_update_list.save_receiver """
        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "lang": self.pagemeta.lang,
            "object_url": self.get_absolute_url(),
            "title": self.get_title()
        }

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.pagemeta.title or self.pagemeta.page.slug

    def save(self, *args, **kwargs):
        if self.pagemeta.page.page_type != PageTree.PAGE_TYPE:
            # FIXME: Better error with django model validation?
            raise AssertionError("PageContent can only exist on a page type tree entry!")
        return super(PageContent, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PageContent '%s' (%s)" % (self.pagemeta.page.slug, self.pagemeta.lang)

    class Meta:
        verbose_name_plural = verbose_name = "PageContent"
        ordering = ("-lastupdatetime",)
#        ordering = ("page", "lang")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageContent)

signals.post_save.connect(receiver=page_update_list.save_receiver, sender=PageContent)

#------------------------------------------------------------------------------

class ColorScheme(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        site    -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    name = models.CharField(max_length=255, help_text="The name of this color scheme.")

    def update(self, colors):
        assert isinstance(colors, dict)
        new = []
        updated = []
        exists = []
        for name, value in colors.iteritems():
            color, created = Color.objects.get_or_create(
                colorscheme=self, name=name,
                defaults={"colorscheme":self, "name":name, "value":value}
            )
            if created:
                new.append(color)
            elif color.value != value:
                color.value = value
                updated.append(color)
                color.save()
            else:
                exists.append(color)
        return new, updated, exists

    def __unicode__(self):
        sites = [site.name for site in self.site.all()]
        return u"ColorScheme '%s' (on sites: %r)" % (self.name, sites)

class ColorManager(models.Manager):
    def get_color_dict(self, colorscheme):
        colors = self.all().filter(colorscheme=colorscheme)
        color_list = colors.values_list('name', 'value')
        return dict([(name, "#%s" % value) for name, value in color_list])

class Color(AutoSiteM2M, UpdateInfoBaseModel):
    """
    inherited attributes from AutoSiteM2M:
        site    -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    objects = ColorManager()

    colorscheme = models.ForeignKey(ColorScheme)
    name = models.CharField(max_length=128,
        help_text="Name if this color (e.g. main_color, head_background)"
    )
    value = ColorValueField(help_text="CSS hex color value.")

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" ", "_")
        new_name = self.name
        try:
            old_name = Color.objects.get(id=self.id).name
        except Color.DoesNotExist:
            # New color
            pass
        else:
            if new_name != old_name:
                # Color name has been changed -> Rename template placeholder in every headfile, too.
                designs = Design.objects.all().filter(colorscheme=self.colorscheme)
                for design in designs:
                    headfiles = design.headfiles.all()
                    for headfile in headfiles:
                        if headfile.render != True: # File used no color placeholder
                            continue

                        old_content = headfile.content
                        # FIXME: Use flexibler regexp. for this:
                        new_content = old_content.replace("{{ %s }}" % old_name, "{{ %s }}" % new_name)
                        if old_content == new_content:
                            # content not changed?!?
                            failsafe_message(
                                "Color '{{ %s }}' not exist in headfile %r" % (old_name, headfile)
                            )
                            continue

                        if settings.DEBUG:
                            failsafe_message(
                                "change color name from '%s' to '%s' in %r" % (old_name, new_name, headfile)
                            )
                        headfile.content = new_content
                        headfile.save()

        return super(Color, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Color '%s' #%s (%s)" % (self.name, self.value, self.colorscheme)

    class Meta:
        unique_together = (("colorscheme", "name"),)
        ordering = ("colorscheme", "name")

#------------------------------------------------------------------------------

class DesignManager(models.Manager):
    pass

class Design(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Page design: template + CSS/JS files

    inherited attributes from AutoSiteM2M:
        site    -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = DesignManager()

    name = models.CharField(unique=True, max_length=150, help_text="Name of this design combination",)
    template = models.CharField(max_length=128, help_text="filename of the used template for this page")
    headfiles = models.ManyToManyField("EditableHtmlHeadFile", null=True, blank=True,
        help_text="Static files (stylesheet/javascript) for this page, included in html head via link tag"
    )
    colorscheme = models.ForeignKey(ColorScheme, null=True, blank=True)

    def save(self, *args, **kwargs):
        assert isinstance(self.template, basestring), \
            "Template must be name as a String, not a template instance!"

        return super(Design, self).save(*args, **kwargs)

    def __unicode__(self):
        sites = self.site.values_list('name', flat=True)
        return u"Page design '%s' (on sites: %r)" % (self.name, sites)

    class Meta:
        ordering = ("template",)


#------------------------------------------------------------------------------

class EditableHtmlHeadFileManager(models.Manager):
    def get_HeadfileLink(self, filename):
        """
        returns a pylucid.system.headfile.Headfile instance
        """
        db_instance = self.get(filename=filename)
        return headfile.HeadfileLink(filename=db_instance.filename)#, content=db_instance.content)


class EditableHtmlHeadFile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Storage for editable static text files, e.g.: stylesheet / javascript.

    inherited attributes from AutoSiteM2M:
        site    -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = EditableHtmlHeadFileManager()

    filepath = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=64)
    html_attributes = models.CharField(max_length=256, null=False, blank=True,
        # TODO: Use this!
        help_text='Additional html tag attributes (CSS example: media="screen")'
    )
    render = models.BooleanField(default=False,
        help_text="Are there CSS ColorScheme entries in the content?"
    )
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    def get_color_filepath(self, colorscheme=None):
        """ Colorscheme + filepath """
        if colorscheme:
            assert isinstance(colorscheme, ColorScheme)
            return os.path.join("ColorScheme_%s" % colorscheme.pk, self.filepath)
        else:
            # The Design used no colorscheme
            return self.filepath

    def get_path(self, colorscheme):
        """ Path for filesystem cache path and link url. """
        return os.path.join(
            settings.PYLUCID.PYLUCID_MEDIA_DIR, settings.PYLUCID.CACHE_DIR,
            self.get_color_filepath(colorscheme)
        )

    def get_cachepath(self, colorscheme):
        """
        filesystem path with filename.
        TODO: Install section sould create the directories!
        """
        return os.path.join(settings.MEDIA_ROOT, self.get_path(colorscheme))

    def get_rendered(self, colorscheme):
        color_dict = Color.objects.get_color_dict(colorscheme)
        return render.render_string_template(self.content, color_dict)

    def save_cache_file(self, colorscheme):
        """
        Try to cache the head file into filesystem (Only worked, if python process has write rights)
        Try to create the out path, if it's not exist.
        """
        cachepath = self.get_cachepath(colorscheme)

        def _save_cache_file(auto_create_dir=True):
            rendered_content = self.get_rendered(colorscheme)
            try:
                f = file(cachepath, "w")
                f.write(rendered_content)
                f.close()
            except IOError, err:
                if auto_create_dir and err.errno == errno.ENOENT: # No 2: No such file or directory
                    # Try to create the out dir and save the cache file
                    path = os.path.dirname(cachepath)
                    if not os.path.isdir(path):
                        # Try to create cache path and save file
                        os.makedirs(path)
                        failsafe_message("Cache path %s created" % path)
                        _save_cache_file(auto_create_dir=False)
                        return
                raise

        try:
            _save_cache_file()
        except (IOError, OSError), err:
            failsafe_message("Can't cache EditableHtmlHeadFile into %r: %s" % (cachepath, err))
        else:
            if settings.DEBUG:
                failsafe_message("EditableHtmlHeadFile cached successful into: %r" % cachepath)

    def save_all_color_cachefiles(self):
        """
        this headfile was changed: resave all cache files in every existing colors
        TODO: Update Queyset lookup
        """
        designs = Design.objects.all()
        for design in designs:
            headfiles = design.headfiles.all()
            for headfile in headfiles:
                if headfile == self:
                    colorscheme = design.colorscheme
                    self.save_cache_file(colorscheme)

    def get_absolute_url(self, colorscheme):
        cachepath = self.get_cachepath(colorscheme)
        if os.path.isfile(cachepath):
            # The file exist in media path -> Let the webserver send this file ;)
            return os.path.join(settings.MEDIA_URL, self.get_path(colorscheme))
        else:
            # not cached into filesystem -> use pylucid.views.send_head_file for it
            url = reverse('PyLucid-send_head_file', kwargs={"filepath":self.filepath})
            if colorscheme:
                return url + "?ColorScheme=%s" % colorscheme.pk
            else:
                # Design used no colorscheme
                return url

    def get_headfilelink(self, colorscheme):
        """ Get the link url to this head file. """
        url = self.get_absolute_url(colorscheme)
        return headfile.HeadfileLink(url)

    def auto_mimetype(self):
        """ returns the mimetype for the current filename """
        fileext = os.path.splitext(self.filepath)[1].lower()
        if fileext == ".css":
            return u"text/css"
        elif fileext == ".js":
            return u"text/javascript"
        else:
            mimetypes.guess_type(self.filepath)[0] or u"application/octet-stream"

    def save(self, *args, **kwargs):
        if self.id == None: # new item should be created.
            # manually check a unique togeher, because django can't do this with a M2M field.
            # Obsolete if unique_together work with ManyToMany: http://code.djangoproject.com/ticket/702
            exist = EditableHtmlHeadFile.on_site.filter(filepath=self.filepath).count()
            if exist != 0:
                from django.db import IntegrityError
                # We can use attributes from this model instance, because it needs to have a primary key
                # value before a many-to-many relationship can be used.
                site = Site.objects.get_current()
                raise IntegrityError(
                    "EditableHtmlHeadFile with same filepath exist on site %r" % site
                )

        if not self.mimetype:
            # autodetect mimetype
            self.mimetype = self.auto_mimetype()

        # Try to cache the head file into filesystem (Only worked, if python process has write rights)
        self.save_all_color_cachefiles()

        return super(EditableHtmlHeadFile, self).save(*args, **kwargs)

    def __unicode__(self):
        sites = [site.name for site in self.site.all()]
        return u"'%s' (on sites: %r)" % (self.filepath, sites)

    class Meta:
        #unique_together = ("filepath", "site")
        # unique_together doesn't work with ManyToMany: http://code.djangoproject.com/ticket/702
        ordering = ("filepath",)





class UserProfile(AutoSiteM2M, UpdateInfoBaseModel):
    """
    Stores additional information about PyLucid users
    http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users

    Created via post_save signal, if a new user created.

    inherited attributes from AutoSiteM2M:
        site    -> ManyToManyField to Site
        on_site -> sites.managers.CurrentSiteManager instance
    """
    user = models.ForeignKey(User, unique=True, related_name="%(class)s_user")

    sha_login_checksum = models.CharField(max_length=192,
        help_text="Checksum for PyLucid JS-SHA-Login"
    )
    sha_login_salt = models.CharField(max_length=5,
        help_text="Salt value for PyLucid JS-SHA-Login"
    )

    # TODO: Overwrite help_text:
#    site = models.ManyToManyField(Site,
#        help_text="User can access only these sites."
#    )

    def set_sha_login_password(self, raw_password):
        """
        create salt+checksum for JS-SHA-Login.
        see also: http://www.pylucid.org/_goto/8/JS-SHA-Login/
        """
        raw_password = str(raw_password)
        salt, sha_checksum = crypt.make_sha_checksum2(raw_password)
        self.sha_login_salt = salt
        self.sha_login_checksum = sha_checksum
        failsafe_message("SHA Login salt+checksum set for user '%s'." % self.user)

    def __unicode__(self):
        return u"UserProfile for user '%s'" % self.user.username

    class Meta:
        ordering = ("user",)


#______________________________________________________________________________

def cache_headfiles(sender, **kwargs):
    """
    One colorscheme was changes: resave all cache headfiles with new color values.
    """
    colorscheme = kwargs["instance"]

    designs = Design.objects.all().filter(colorscheme=colorscheme)
    for design in designs:
        headfiles = design.headfiles.all()
        for headfile in headfiles:
            headfile.save_cache_file(colorscheme)

signals.post_save.connect(cache_headfiles, sender=ColorScheme)

#______________________________________________________________________________
# Create user profile via signals

def create_user_profile(sender, **kwargs):
    """ signal handler: creating user profile, after a new user created. """
    user = kwargs["instance"]

    userprofile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        failsafe_message("UserProfile entry for user '%s' created." % user)
#
#        if not user.is_superuser: # Info: superuser can automaticly access all sites
#            site = Site.objects.get_current()
#            userprofile.site.add(site)
#            failsafe_message("Add site '%s' to '%s' UserProfile." % (site.name, user))

signals.post_save.connect(create_user_profile, sender=User)


#______________________________________________________________________________
"""
We make a Monkey-Patch and change the method set_password() from
the model class django.contrib.auth.models.User.
We need the raw plaintext password, this is IMHO not available via signals.
"""

# Save the original method
orig_set_password = User.set_password


def set_password(user, raw_password):
    #print "set_password() debug:", user, raw_password
    if user.id == None:
        # It is a new user. We must save the django user accound first to get a
        # existing user object with a ID and then the JS-SHA-Login Data can assign to it.
        user.save()

    # Use the original method to set the django User password:
    orig_set_password(user, raw_password)

    userprofile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        failsafe_message("UserProfile entry for user '%s' created." % user)

    # Save the password for the JS-SHA-Login:
    userprofile.set_sha_login_password(raw_password)
    userprofile.save()


# replace the method
User.set_password = set_password
