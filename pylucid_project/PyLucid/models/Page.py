# -*- coding: utf-8 -*-
"""
    PyLucid.models.Page
    ~~~~~~~~~~~~~~~~~~~

    Models for Page and PageArchive

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from PyLucid.system.utils import get_uri_base
from PyLucid.tools.shortcuts import getUniqueShortcut
from PyLucid.system.exceptions import AccessDenied, LowLevelError


MARKUPS = (
    (0, u'html'),
    (1, u'html + TinyMCE'),
    (2, u'textile'),
    (3, u'Textile (original)'),
    (4, u'Markdown'),
    (5, u'ReStructuredText'),
    (6, u'Creole wiki markup'),
)


class PageManager(models.Manager):
    """
    Manager for Page model.
    """

    class WrongShortcut(LookupError):
        """ URL string contained invalid shortcuts at the end. """
        pass

    @property
    def default_page(self):
        """ Return default "index" page """
        from PyLucid.models import Plugin
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
            page_id = preferences["index_page"]
            return self.get(id__exact=page_id)
        except Exception, e:
            # The defaultPage-ID from the Preferences is wrong! Return first
            # page if anything exists.
            try:
                return self.all().order_by("parent", "position")[0]
            except IndexError, e:
                msg = _("Error getting a cms page.")
                raise LowLevelError(msg, e)

    def _check_permission_tree(self,page,test_fcn):
        """
        Check permissions of page and its parents. The second parameter
        test_fcn(page_object) is the test function which must return true or false
        corresponding to permssion to view specific page.
        """
        while page:
            if not test_fcn(page):
                return False
            page = page.parent
        return True

    def __check_publicView(self, page):
        """
        Return true/false if page permits anonymous view.
        """
        return page.permitViewPublic

    def __check_groupView(self, user_group_ids):
        """
        Return true/false if page permits anonymous view.
        """
        def check(page):
            if page.permitViewGroup == None:
                return True
            else:
                return page.permitViewGroup.id in user_group_ids
        return check


    def get_by_shortcut(self,url_shortcuts,user):
        """
        Returns a page object matching the shortcut.

        PyLucid urls are build from the page shortcuts:
        domain.tld/shortcut1/shortcut2/. Only the last existing shortcut will
        be used. All other parts of the url are simply ignored.

        If url_shortcuts contains no shortcut -> Return the default page (stored in the
        Preference table).
        If a part of the url is wrong -> Raise WrongShortcut, with correct path in message
        If a anonymous user would get a permitViewPublic page -> Raise AccessDenied.
        If no matching page is found -> Raise Page.DoesNotExist

        TODO: Support user group based access control.
        """

        # /shortcut1/shortcut2/ -> ['shortcut1','shortcut2']
        shortcuts = url_shortcuts.strip("/").split('/')

        if shortcuts[0] == "":
            # No shortcuts return default_page
            return self.default_page

        # Check shortcuts in reversed order
        shortcuts.reverse()
        wrong_shortcut = False
        if not user.is_anonymous():
            user_groups = [x['id'] for x in user.groups.all().values('id')]
        for shortcut in shortcuts:
            try:
                page = self.select_related().get(shortcut__exact=shortcut)
            except self.model.DoesNotExist:
                wrong_shortcut = True
                continue
            if user.is_anonymous():
                if not self._check_permission_tree(page,self.__check_publicView):
                    # the page or its parent is not viewable for anonymous user
                    raise AccessDenied
            elif not user.is_superuser:
                # Superuser can see all pages.
                if not self._check_permission_tree(page,self.__check_groupView(user_groups)):
                    # User is logged in. Check if page is restricted to user group
                    raise AccessDenied

            # Found an existing, viewable page
            if wrong_shortcut:
                # At least one of the shortcuts in the url was wrong -> raise
                raise self.WrongShortcut, page.get_absolute_url()
            return page
        # No right page found
        raise self.model.DoesNotExist

    def get_update_info(self, hide_non_public=True):
        """
        returns a "last updated pages" queryset.
        Used e.g. in RSSfeedGenerator, page_update_list
        """
        pages = Page.objects.order_by('-lastupdatetime')

        if hide_non_public:
            pages = pages.filter(showlinks = True)
            pages = pages.exclude(permitViewPublic = False)

        return pages

#______________________________________________________________________________

class Page(models.Model):
    """
    A CMS Page Object

    TODO: We should refactor the "pre_save" behavior, use signals:
    http://code.djangoproject.com/wiki/Signals
    """

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
        max_length=1, choices=MARKUPS,
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

    def _check_default_page_settings(self):
        """
        The default page must have some settings.
        """
        from PyLucid.models import Plugin
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
        except Plugin.DoesNotExist, e:
            # Update old PyLucid installation?
            return

        index_page_id = preferences["index_page"]

        if index_page_id == None:
            # No default page definied
            return

        if int(self.id) != int(index_page_id):
            # This page is not the default index page
            return

        #______________________________________________________________________
        # Check some settings for the default index page:

        assert self.permitViewPublic == True, (
            "Error save the new page data:"
            " The default page must be viewable for anonymous users."
            " (permitViewPublic must checked.)"
        )
        assert self.showlinks == True, (
            "Error save the new page data:"
            " The default page must displayed in the main menu."
            " (showlinks must checked.)"
        )

    def _check_parent(self, id):
        """
        Prevents inconsistent data (parent-child-loop).
        Check recusive if a new parent can be attached and is not a loop.
        TODO: This method should used in newform is_valid() ???
        """
        if not self.parent:
            # No parent exist -> root arraived
            return

        if self.parent.id == id:
            # Error -> parent-loop found.
            raise AssertionError("New parent is invalid. (parent-child-loop)")

        # go a level deeper to the root
        self.parent._check_parent(id)

    def _prepare_shortcut(self):
        """
        prepare the page shortcut:
        -rebuild shortcut (maybe)
        -make shortcut unique
        """
        from PyLucid.models import Plugin
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
        except Plugin.DoesNotExist, e:
            # Update old PyLucid installation?
            auto_shortcuts = True
        else:
            auto_shortcuts = preferences["auto_shortcuts"]

        if auto_shortcuts:
            # We should rebuild the shortcut
            self.shortcut = self.name

        #______________________________________________________________________
        # Make a new shortcut unique:

        if self.id != None:# A existing page should update
            # Exclude the existing shortcut from the "black list":
            exclude_shortcut = Page.objects.get(id=self.id).shortcut
        else: # A new page created
            exclude_shortcut = None

        self.shortcut = getUniqueShortcut(self.shortcut, exclude_shortcut)

    def save(self):
        """
        Save a new page or update changed page data.
        before save: check some data consistency to prevents inconsistent data.
        """
        from PyLucid.system.utils import delete_page_cache
        if self.id != None:
            # a existing page should be updated (It's not a new page ;)

            # Check some settings for the default index page:
            self._check_default_page_settings()

            # check if a new parent is no parent-child-loop:
            self._check_parent(self.id)

        # Delete all pages in the cache.
        # FIXME: This is only needed, if the menu changed: e.g.: if the page
        # position, shortcut, parent cahnges...
        delete_page_cache()

        # name and shortcut can be None, for make shortcut unique
        if self.name == None:
            self.name = ""
        if self.shortcut == None:
            self.shortcut = ""

        # Rebuild shortcut / make shortcut unique:
        self._prepare_shortcut()

        # Delete old page cache, if exist
        cache_key = settings.PAGE_CACHE_PREFIX + self.shortcut
        cache.delete(cache_key)

        super(Page, self).save() # Call the "real" save() method

    def delete(self):
        # Delete all pages in the cache.
        from PyLucid.system.utils import delete_page_cache
        delete_page_cache()
        super(Page, self).delete()

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

    def get_absolute_uri(self):
        """
        returned the complete absolute URI (with the domain/host part)
        """
        url = self.get_absolute_url()
        uri_base = get_uri_base()
        return uri_base + url

    def get_permalink(self):
        uri_base = get_uri_base()
        prefix = getattr(settings, "PERMALINK_URL_PREFIX", "_goto")
        return "%s/%s/%s/%s/" % (uri_base, prefix, self.id, self.shortcut)


    def get_verbose_title(self):
        """
        TODO: Should we handle name and title on a other way...
        """
        if self.title and self.title != self.name:
            return self.name + " - " + self.title
        else:
            return self.name

    def __strftime(self, datetime_obj):
        if datetime_obj == None:
            return "[unknown]"
        else:
            return datetime_obj.strftime(_("%Y-%m-%d - %H:%M"))

    def get_createtime_string(self):
        return self.__strftime(self.createtime)

    def get_lastupdatetime_string(self):
        return self.__strftime(self.lastupdatetime)

    def __unicode__(self):
        return self.shortcut


class PageAdmin(admin.ModelAdmin):
    list_display = (
        "id", "shortcut", "name", "title", "description",
        "lastupdatetime", "lastupdateby"
    )
    list_display_links = ("shortcut",)
    list_filter = (
        "createby","lastupdateby","permitViewPublic", "template", "style"
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ["content", "name", "title", "description", "keywords"]

    # FIXME:
#    fields = (
#
#        ('meta', {'fields': ('keywords', 'description')}),
#        ('name / shortcut / title', {
#            'classes': 'collapse',
#            'fields': ('name','shortcut','title')
#        }),
#        ('template / style / markup', {
#            'classes': 'collapse',
#            'fields': ('template','style','markup')
#        }),
#        ('Advanced options', {
#            'classes': 'collapse',
#            'fields' : (
#                'showlinks', 'permitViewPublic',
#                'permitViewGroup', 'permitEditGroup'
#            ),
#        }),
#    )
#    fieldsets = (
#        ('basic', {'fields': ('content','parent','position',)}),
#    )


admin.site.register(Page, PageAdmin)

#______________________________________________________________________________

class PageArchiv(models.Model):
    """
    A simple archiv for old cms page content.
    """
    # Explicite id field, so we can insert a help_text ;)
    id = models.AutoField(primary_key=True, help_text="The internal page ID.")

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "Page", to_field="id", related_name="PageArchiv_parent",
        null=True, blank=True,
        help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default = 0,
        help_text = "ordering weight for sorting the pages in the menu."
    )

    name = models.CharField(max_length=150, help_text="A short page name")

    shortcut = models.CharField(
        max_length=150, help_text="shortcut to built the URLs"
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
        max_length=1, choices=MARKUPS,
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
        User, editable=False, related_name="pageachiv_createby",
        help_text="User how create the current page.",
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, related_name="pageachiv_lastupdateby",
        help_text="User as last edit the current page.",
    )

    showlinks = models.BooleanField(default=True,
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )
    permitViewPublic = models.BooleanField(default=True,
        help_text="Can anonymous see this page?"
    )

    permitViewGroup = models.ForeignKey(
        Group, related_name="pageachiv_permitViewGroup", null=True, blank=True,
        help_text="Limit viewable to a group?"
    )

    permitEditGroup = models.ForeignKey(
        Group, related_name="pageachiv_permitEditGroup", null=True, blank=True,
        help_text="Usergroup how can edit this page."
    )

    page = models.ForeignKey("Page",
        help_text="relationship to the original page entry"
    )
    edit_comment = models.CharField(
        blank=True, max_length=255,
        help_text="The reason for editing."
    )

    class Meta:
        db_table = 'PyLucid_pagearchiv'
        app_label = 'PyLucid'


class PageArchivAdmin(admin.ModelAdmin):
    list_display = (
        "id", "page", "edit_comment",
        "shortcut", "name", "title",
        "description", "lastupdatetime", "lastupdateby"
    )

admin.site.register(PageArchiv, PageArchivAdmin)