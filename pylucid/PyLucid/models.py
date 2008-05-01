# -*- coding: utf-8 -*-

"""
    PyLucid.models
    ~~~~~~~~~~~~~~

    The database models for PyLucid
    based on Django's ORM.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, posixpath, pickle
from pprint import pformat

from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User, Group, UNUSABLE_PASSWORD
from django.utils.translation import ugettext as _

from PyLucid.tools.newforms_utils import get_init_dict, setup_help_text
from PyLucid.tools.data_eval import data_eval, DataEvalError
from PyLucid.tools.shortcuts import getUniqueShortcut
from PyLucid.tools import crypt
from PyLucid.system.utils import get_uri_base
from PyLucid.system.plugin_import import get_plugin_module

#from PyLucid.db.cache import delete_page_cache


MARKUPS = (
    (0, u'html'),
    (1, u'html + TinyMCE'),
    (2, u'textile'),
    (3, u'Textile (original)'),
    (4, u'Markdown'),
    (5, u'ReStructuredText'),
)

def delete_page_cache():
    """
    Delete all pages in the cache.
    Needed, if:
        - A template has been edited
        - The menu changes (edit the page name, position, parent link)
    TODO: move this function from models.py into a other nice place...
    """
    for items in Page.objects.values('shortcut').iterator():
        shortcut = items["shortcut"]
        cache_key = settings.PAGE_CACHE_PREFIX + shortcut
        cache.delete(cache_key)


class Page(models.Model):
    """
    A CMS Page Object

    TODO: We should refactor the "pre_save" behavior, use signals:
    http://code.djangoproject.com/wiki/Signals
    """
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

    name = models.CharField(max_length=150, help_text="A short page name")

    shortcut = models.CharField(
        unique=True, max_length=150, help_text="shortcut to built the URLs"
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

    class Admin:
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

        fields = (
            ('basic', {'fields': ('content','parent','position',)}),
            ('meta', {'fields': ('keywords', 'description')}),
            ('name / shortcut / title', {
                'classes': 'collapse',
                'fields': ('name','shortcut','title')
            }),
            ('template / style / markup', {
                'classes': 'collapse',
                'fields': ('template','style','markup')
            }),
            ('Advanced options', {
                'classes': 'collapse',
                'fields' : (
                    'showlinks', 'permitViewPublic',
                    'permitViewGroup', 'permitEditGroup'
                ),
            }),
        )

    def _check_default_page_settings(self):
        """
        The default page must have some settings.
        """
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
        except Plugin.DoesNotExist, e:
            # Update old PyLucid installation?
            return

        index_page_id = preferences["index_page"]

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
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
        except Plugin.DoesNotExist, e:
            # Update old PyLucid installation?
            auto_shortcuts = True
        else:
            print ">>>", preferences
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

        # Rebuild shortcut / make shortcut unique:
        self._prepare_shortcut()

        # Delete old page cache, if exist
        cache_key = settings.PAGE_CACHE_PREFIX + self.shortcut
        cache.delete(cache_key)

        super(Page, self).save() # Call the "real" save() method

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


#______________________________________________________________________________

class PageArchiv(models.Model):
    """
    A simple archiv for old cms page content.
    """
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

    class Admin:
        list_display = (
            "id", "page", "edit_comment", "shortcut", "name", "title",
            "description", "lastupdatetime", "lastupdateby"
        )

#______________________________________________________________________________


class JS_LoginData(models.Model):
    """
    This model class stores the needed SHA information for the PyLucid
    JS-SHA-Login.
    Note: We make a Monkey-Patch (?) and change the method set_password() from
    the model class django.contrib.auth.models.User
    """
    user = models.ForeignKey(User)

    sha_checksum = models.CharField(max_length=192)
    salt = models.CharField(max_length=5)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    def set_unusable_password(self):
        self.salt = UNUSABLE_PASSWORD
        self.sha_checksum = UNUSABLE_PASSWORD

    def set_password(self, raw_password):
        raw_password = str(raw_password)
        salt, sha_checksum = crypt.make_sha_checksum2(raw_password)
        self.salt = salt
        self.sha_checksum = sha_checksum

    def __unicode__(self):
        return self.user.username

    class Admin:
        list_display = (
            'user', 'sha_checksum', 'salt', 'createtime', 'lastupdatetime'
        )

    class Meta:
        verbose_name = verbose_name_plural = 'JS-LoginData'



# Save the original method
old_set_password = User.set_password

def set_password(user, raw_password):
#    print "set_password() debug:", user, raw_password
    if user.id == None:
        # It is a new user. We must save the django user accound first to get a
        # existing user object with a ID and then the JS_LoginData can assign to it.
        user.save()

    # Save the password for the JS-SHA-Login:
    login_data, status = JS_LoginData.objects.get_or_create(user = user)
    login_data.set_password(raw_password)
    login_data.save()

    # Use the original method to set the django User password:
    old_set_password(user, raw_password)


# Make a hook into Django's default way to set a new User Password.
# Get the new raw_password and set the PyLucid password, too.
User.set_password = set_password

#____________________________________________________________________


class Preference(models.Model):
    # Obsolete!
    pass

#____________________________________________________________________

preference_cache = {}

class PluginManager(models.Manager):
    def get_preferences(self, plugin_name):
        """
        returns the preference data dict, use the cache
        """
        # Get the name of the plugin, if __file__ used
        plugin_name = os.path.splitext(os.path.basename(plugin_name))[0]
        print "plugin name: '%s'" % plugin_name

        if plugin_name in preference_cache:
            return preference_cache[plugin_name]

        plugin = self.get(plugin_name = plugin_name)
        return plugin.get_preferences()


class Plugin(models.Model):
    objects = PluginManager()

    plugin_name = models.CharField(max_length=90, unique=True)

    package_name = models.CharField(max_length=255)
    author = models.CharField(blank=True, max_length=150)
    url = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=255)

    pref_data_string = models.TextField(
        null=True, blank=True,
        help_text="printable representation of the newform data dictionary"
    )
    can_deinstall = models.BooleanField(default=True,
        help_text=(
            "If false and/or not set:"
            " This essential plugin can't be deinstalled."
        )
    )
    active = models.BooleanField(default=False,
        help_text="Is this plugin is enabled and useable?"
    )

    def init_pref_form(self, pref_form):
        """
        Set self.pref_data_string from the given newforms form and his initial
        values.
        """
        init_dict = get_init_dict(pref_form)
        preference_cache[self.plugin_name] = init_dict
        self.set_pref_data_string(init_dict)

    def set_pref_data_string(self, data_dict):
        """
        set the dict via pformat
        """
        preference_cache[self.plugin_name] = data_dict
        self.pref_data_string = pformat(data_dict)

    def get_preferences(self):
        """
        evaluate the pformat string into a dict and return it.
        """
        data_dict = data_eval(self.pref_data_string)
        preference_cache[self.plugin_name] = data_dict
        return data_dict

    def get_pref_form(self, debug):
        """
        Get the 'PreferencesForm' newform class from the plugin modul, insert
        initial information into the help text and return the form.
        """
        plugin_module = get_plugin_module(
            self.package_name, self.plugin_name, debug
        )
        form = getattr(plugin_module, "PreferencesForm")
        setup_help_text(form)
        return form

    def save(self):
        """
        Save a new plugin or update changed data.
        before save: check some data consistency to prevents inconsistent data.
        """
        if self.can_deinstall==False and self.active==False:
            # This plugin can't be deactivaded!
            # If reinit misses, the plugin is deinstalled. After a install with
            # the plugin admin, normaly the plugin would not be acivated
            # automaticly. So we activated it here:
            self.active = True

        super(Plugin, self).save() # Call the "real" save() method

    class Meta:
        permissions = (
            # Permission identifier     human-readable permission name
            ("can_use",                 "Can use the plugin"),
        )

    class Admin:
        list_display = (
            "active", "plugin_name", "description", "can_deinstall"
        )
        list_display_links = ("plugin_name",)
        ordering = ('package_name', 'plugin_name')
        list_filter = ("author","package_name", "can_deinstall")

    def __unicode__(self):
        txt = u"%s - %s" % (self.package_name, self.plugin_name)
        return txt.replace(u"_",u" ")


#______________________________________________________________________________


class Style(models.Model):
    """
    The global stylesheet.
    On save() we try to store the CSS content into a local cache file in the
    media path. This only works, if the process has the writeability.
    In a simple shared web hosting environment, the http server runs the web
    app with the user 'nobody', so he has not the writeability. In this case,
    the stylesheet must be request via a _command url.
    Important: The method get_absolute_url() doesn't check if the local cache
    file was written succsessfully in the past! This it the job for the
    page_style plugin. The method returns allways the url to the locale cache
    file.
    """
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

    class Admin:
        list_display = (
            "id", "name", "description", "createtime", "lastupdatetime"
        )
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name

    def get_filename(self):
        """
        How to make it URL and filesystem save?
        """
        return self.name + ".css"

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part) for the stylesheet
        file stored in the media path.
        Important: Returns allways a link to the locale cache file, it doesn't
        check if the file exists!
        """
        filename = self.get_filename()
        url = posixpath.join(
            "",
            settings.MEDIA_URL,
            settings.PYLUCID_MEDIA_DIR,
            filename, # FIXME: url save?
        )
        return url

    def get_filepath(self):
        """
        Get the file path to the local stylesheet file.
        Important: It is not tested if the file exists!
        FIXME: How to handle special characters?
        """
        filename = self.get_filename()
        filepath = os.path.join(
            settings.MEDIA_ROOT,
            settings.PYLUCID_MEDIA_DIR,
            filename
        )
        # FIXME: Should we use os.path.abspath() ?
        return filepath

    def save(self):
        """
        Save a new or updated stylesheet.
        try to store the content into the cache file in the media path.
        """
        filepath = self.get_filepath()
        try:
            f = file(filepath, "w") # FIXME: Encoding?
            content = self.content.encode(settings.FILE_CHARSET)
            f.write(content)
            f.close()
        except Exception, e:
            # FIXME: How can we give feedback?
#            print "Style save error:", e # Olny for dev server
            pass

        #Delete the page cache if a stylesheet was edited.
        delete_page_cache()

        super(Style, self).save() # Call the "real" save() method


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
        delete_page_cache()

        super(Template, self).save() # Call the "real" save() method

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name
