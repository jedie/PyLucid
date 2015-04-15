# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.http import Http404
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.middlewares import ThreadLocal
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.tree_model import BaseTreeModel, TreeGenerator
from pylucid_migration.base_models.base_models import BaseModel
from pylucid_migration.base_models.permissions import PermissionsBase


class PageTreeManager(models.Manager):
    """
    Manager class for PageTree model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    def get_tree(self, user=None, filter_showlinks=False, exclude_plugin_pages=False, exclude_extras=None, site=None):
        if site is None:
            queryset = self.model.on_site.order_by("position")
        else:
            queryset = self.model.objects.all().filter(site=site).order_by("position")

        if exclude_plugin_pages:
            queryset = queryset.exclude(page_type=PageTree.PLUGIN_TYPE)
        if exclude_extras:
            queryset = queryset.exclude(**exclude_extras)

        items = queryset.values("id", "parent", "slug")
        count=len(items)
        tree = TreeGenerator(items, skip_no_parent=True)
        return count, tree

    def get_root_page(self, user, filter_parent=True):
        """ returns the 'first' root page tree entry witch the user can access """
        queryset = self.all_accessible(user)

        if filter_parent:
            # All "root" pages
            queryset = queryset.filter(parent=None)
        else:
            # fallback if no "root" page is accessable
            queryset = queryset.order_by("parent", "position")

        try:
            return queryset[0]
        except IndexError as err:
            if self.model.on_site.count() == 0:
                raise PageTree.DoesNotExist("There exist no PageTree items!")
            elif filter_parent == True:
                # If all root pages not accessible for the current user
                # -> try to get the first accessable page
                return self.get_root_page(user, filter_parent=False)
            else:
                raise

    def get_pagemeta(self, request, pagetree, show_lang_errors=True):
        """
        return PageMeta instance witch associated to the given >pagetree< instance.
        
        raise PermissionDenied if current user hasn't the pagemeta.permitViewGroup permissions. 
        
        dissolving language in client favored languages
        if not exist:
            return system default language
            
        If show_lang_errors==True:
            create a page_msg if PageMeta doesn't exist in client favored language.
        """
        from pylucid_migration.models.pagemeta import PageMeta  # against import loops.

        # client favored Language instance:
        lang_entry = request.PYLUCID.current_language

        if pagetree.page_type == pagetree.PLUGIN_TYPE:
            # Automatic create a not existing PageMeta on PluginPages
            pagemeta = PageMeta.objects.verbose_get_or_create(
                request, pagetree, lang_entry, show_lang_errors=show_lang_errors
            )
            return pagemeta

        queryset = PageMeta.objects.filter(pagetree=pagetree)
        pagemeta, tried_languages = self.get_by_prefered_language(request, queryset, show_lang_errors=show_lang_errors)

        if pagemeta is None:
            msg = ""
            if settings.DEBUG:
                msg += "This page %r doesn't exist in any languages???" % pagetree
            raise Http404(msg)

        if tried_languages and show_lang_errors and (settings.DEBUG or request.user.is_authenticated()):
            # We should not inform anonymous user, because the page
            # would not caches, if messages exist!
            messages.info(request,
                _(
                    "PageMeta %(slug)s doesn't exist in client"
                    " favored language %(tried_languages)s,"
                    " use %(used_code)s entry."
                ) % {
                    "slug": pagetree.slug,
                    "tried_languages": ", ".join([l.description for l in tried_languages]),
                    "used_code": pagemeta.language.description,
                }
            )

        # Check PageMeta.permitViewGroup permissions:
        # TODO: Check this in unittests!
        if pagemeta.permitViewGroup == None:
            # everyone can't see this page
            return pagemeta
        elif request.user.is_superuser: # Superuser can see everything ;)
            return pagemeta
        elif request.user.is_authenticated() and pagemeta.permitViewGroup in request.user.groups:
            return pagemeta

        # The user is anonymous or is authenticated but is not in the right user group
        raise PermissionDenied


class PageTree(BaseModel, BaseTreeModel, UpdateInfoBaseModel, PermissionsBase):
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
        
    inherited from PermissionsBase:
        validate_permit_group()
        check_sub_page_permissions()
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

    site = models.ForeignKey(Site,
        #default=Site.objects.get_current
        default=settings.SITE_ID,
    )
    on_site = CurrentSiteManager()

    page_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    design = models.ForeignKey("pylucid_migration.Design", help_text="Page Template, CSS/JS files")

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

    def recusive_attribute(self, attribute):
        """
        Goes the pagetree back to root and return the first match of attribute if not None.
        
        used e.g.
            with permitViewGroup and permitEditGroup
            from self.validate_permit_group() and self.check_sub_page_permissions()
        """
        parent = self.parent
        if parent is None: # parent is the tree root
            return None

        if getattr(parent, attribute) is not None:
            # the attribute was set by parent page
            return parent
        else:
            # go down to root
            return parent.recusive_attribute(attribute)

    def get_absolute_url(self):
        """ absolute url *without* language code (without domain/host part) """
        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            url = parent_shortcut + self.slug + "/"
        else:
            url = "/" + self.slug + "/"

        return url

    def get_absolute_uri(self):
        """ absolute url with domain/host part (but without language code) """
        absolute_url = self.get_absolute_url()
        domain = self.site.domain
        return "http://" + domain + absolute_url

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.site

    def __unicode__(self):
        return u"PageTree %r (id: %i, site: %s, type: %s)" % (
            self.slug, self.id, self.site.domain, self.TYPE_DICT.get(self.page_type)
        )

    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'pylucid_pagetree'
        verbose_name_plural = verbose_name = "PageTree"
        unique_together = (("site", "slug", "parent"),)

        # FIXME: It would be great if we can order by get_absolute_url()
#        ordering = ("site", "id", "position")
        ordering = ("-lastupdatetime",)



