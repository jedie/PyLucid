# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.middlewares import ThreadLocal
from django_tools.tagging_addon.fields import jQueryTagModelField
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.base_models.base_models import BaseModelManager, BaseModel
from pylucid_project.base_models.permissions import PermissionsBase


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



class CurrentSiteManager(models.Manager):
    """
    Use this to limit objects to those associated with the current site.
    Based on django.contrib.sites.managers.CurrentSiteManager()
    """
    def get_query_set(self):
        queryset = super(CurrentSiteManager, self).get_query_set()
        return queryset.filter(pagetree__site__id__exact=settings.SITE_ID)


class PageMetaManager(BaseModelManager):
    """
    inherited from BaseModelManager:
        easy_create()
    """
    def verbose_get_or_create(self, request, pagetree, lang_entry, show_lang_errors=True):
        """
        returns PageMeta, create it if not exist.
        
        If show_lang_errors==True:
            create a page_msg if PageMeta doesn't exist in client favored language.
        """
        if settings.DEBUG:
            assert pagetree.page_type == pagetree.PLUGIN_TYPE, "should only used for PluginPages!"

        pagemeta, created = self.model.on_site.get_or_create(pagetree=pagetree, language=lang_entry)
        if created:
            msg = "auto create %s" % pagemeta

            from pylucid_project.apps.pylucid.models import LogEntry # against import loops.
            LogEntry.objects.log_action(
                app_label="pylucid", action="auto create PageMeta", request=request, message=msg
            )
            if show_lang_errors or settings.DEBUG or request.user.is_superuser:
                messages.info(request, msg)

        return pagemeta


class PageMeta(BaseModel, UpdateInfoBaseModel, PermissionsBase):
    """
    Meta data for PageContent or PluginPage

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who created this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
        
    inherited from PermissionsBase:
        validate_permit_group()
        check_sub_page_permissions()
    """
    objects = PageMetaManager()
    on_site = CurrentSiteManager()

    pagetree = models.ForeignKey("pylucid.PageTree") # Should we add null=True, blank=True here? see clean_fields() below
    language = models.ForeignKey("pylucid.Language")

    name = models.CharField(blank=True, max_length=150,
        help_text="Sort page name (for link text in e.g. menu)"
    )
    title = models.CharField(blank=True, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )

    tags = jQueryTagModelField() # a django-tagging model field modified by django-tools

    keywords = models.CharField(blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(blank=True, max_length=255, help_text="For html header")

    robots = models.CharField(blank=True, max_length=255, default="index,follow",
        help_text="for html 'robots' meta content."
    )

    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable this page in this language to a user group?",
        null=True, blank=True,
    )
    # FIXME: Add permitEditGroup, too.
    # e.g.: allow only usergroup X to edit this page in language Y
    # https://github.com/jedie/PyLucid/issues/57

    def clean_fields(self, exclude):
        super(PageMeta, self).clean_fields(exclude)

        message_dict = {}

        try:
            # We can only check the sub pages, if exists ;)
            pagetree = self.pagetree
        except ObjectDoesNotExist:
            # FIXME: Should self.pagetree() field has null=True, blank=True ?
            return

        # Prevents that a unprotected page created below a protected page.
        # TODO: Check this in unittests
        # validate_permit_group() method inherited from PermissionsBase
        self.validate_permit_group("permitViewGroup", exclude, message_dict)

        # Warn user if PageMeta permissions mismatch with sub pages
        # TODO: Check this in unittests
        queryset = PageMeta.objects.filter(pagetree__parent=self.pagetree)
        self.check_sub_page_permissions(# method inherited from PermissionsBase
            ("permitViewGroup",), # TODO: permitEditGroup, read above
            exclude, message_dict, queryset
        )

        if message_dict:
            raise ValidationError(message_dict)

    def recusive_attribute(self, attribute):
        """
        Goes the pagetree back to root and return the first match of attribute if not None.
        
        used e.g.
            with permitViewGroup and permitEditGroup
            from self.validate_permit_group() and self.check_sub_page_permissions()
        """
        parent_pagetree = self.pagetree.parent
        if parent_pagetree is None: # parent is the tree root
            return None

        request = ThreadLocal.get_current_request()
        if request is None:
            # Check only if we are in a request
            return

        queryset = PageMeta.objects.filter(pagetree=parent_pagetree)
        parent_pagemeta = None
        languages = request.PYLUCID.languages # languages are in client prefered order
        for language in languages:
            try:
                parent_pagemeta = queryset.get(language=language)
            except PageMeta.DoesNotExist:
                continue
            else:
                break

        if parent_pagemeta is None:
            return

        if getattr(parent_pagemeta, attribute) is not None:
            # the attribute was set by parent page
            return parent_pagemeta
        else:
            # go down to root
            return parent_pagemeta.recusive_attribute(attribute)

    _url_cache = LocalSyncCache(id="PageMeta_absolute_url")
    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        if self.pk in self._url_cache:
            #print "PageMeta url cache len: %s, pk: %s" % (len(self._url_cache), self.pk)
            return self._url_cache[self.pk]

        lang_code = self.language.code
        page_url = self.pagetree.get_absolute_url()
        url = "/" + lang_code + page_url

        self._url_cache[self.pk] = url
        return url

    _permalink_cache = LocalSyncCache(id="PageMeta_permalink")
    def get_permalink(self):
        """
        return a permalink. Use page slug/name/title or nothing as additional text.
        """
        if self.pk in self._permalink_cache:
            #print "PageMeta permalink_cache len: %s, pk: %s" % (len(self._permalink_cache), self.pk)
            return self._permalink_cache[self.pk]

        # Get the system preferences
        request = ThreadLocal.get_current_request()
        sys_pref = request.PYLUCID.preferences
        sys_pref_form = request.PYLUCID.preferences_form

        use_additions = sys_pref.get("permalink_additions", sys_pref_form.PERMALINK_USE_TITLE)

        do_slugify = False
        if use_additions == sys_pref_form.PERMALINK_USE_TITLE:
            # Append the PageMeta title (language dependent)
            addition_txt = self.get_title()
            do_slugify = True
        elif use_additions == sys_pref_form.PERMALINK_USE_NAME:
            addition_txt = self.get_name()
            do_slugify = True
        elif use_additions == sys_pref_form.PERMALINK_USE_SLUG:
            addition_txt = self.pagetree.slug
        else:
            addition_txt = ""

        if do_slugify:
            addition_txt = slugify(addition_txt)

        url = reverse('PyLucid-permalink', kwargs={'page_id': self.pagetree.id, 'url_rest': addition_txt})
        self._permalink_cache[self.pk] = url
        return url

    def save(self, *args, **kwargs):
        """ reset PageMeta and PageTree url cache """
        # Clean the local url cache dict
        self._url_cache.clear()
        self._permalink_cache.clear()
        self.pagetree._url_cache.clear()

        # FIXME: We must only update the cache for the current SITE not for all sites.
        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

        return super(PageMeta, self).save(*args, **kwargs)

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.pagetree.site
    get_site.short_description = _('on site')
    get_site.allow_tags = False

    def get_other_languages(self):
        return PageMeta.objects.all().filter(pagetree=self.pagetree).exclude(language=self.language)

    def get_title(self):
        """ The page title is optional, if not exist, used the slug from the page tree """
        return self.title or self.get_name()

    def get_name(self):
        return self.name or self.pagetree.slug

    def __unicode__(self):
        return u"PageMeta for page: %r (lang: %s, site: %s)" % (
            self.pagetree.slug, self.language.code, self.get_site().domain
        )

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PageMeta"
        unique_together = (("pagetree", "language"),)
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageMeta)
