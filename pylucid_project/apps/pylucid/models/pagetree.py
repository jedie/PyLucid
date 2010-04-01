# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
from xml.sax.saxutils import escape

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal
from django_tools import model_utils

from pylucid_project.apps.pylucid.tree_model import BaseTreeModel, TreeGenerator
from pylucid_project.apps.pylucid.models.base_models import BaseModel, BaseModelManager, UpdateInfoBaseModel


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



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

    def all_accessible(self, user=None, filter_showlinks=False):
        """ returns all pages that the given user can access. """
        if user == None:
            user = ThreadLocal.get_current_user()

        queryset = self.model.on_site.order_by("position")
        queryset = self.filter_accessible(queryset, user)

        if filter_showlinks:
            # Filter PageTree.showlinks
            queryset = queryset.filter(showlinks=True)

        return queryset

    def get_tree(self, user=None, filter_showlinks=False, exclude_plugin_pages=False, exclude_extras=None):
        """ return a TreeGenerator instance with all accessable page tree instance """
        queryset = self.all_accessible(user, filter_showlinks)

        if exclude_plugin_pages:
            queryset = queryset.exclude(page_type=PageTree.PLUGIN_TYPE)
        if exclude_extras:
            queryset = queryset.exclude(**exclude_extras)

        items = queryset.values("id", "parent", "slug")
        tree = TreeGenerator(items, skip_no_parent=True)
        return tree

    def get_choices(self, user=None, exclude_extras=None):
        """ returns a choices list for e.g. a forms select widget. """
        tree = PageTree.objects.get_tree(user, exclude_plugin_pages=True, exclude_extras=exclude_extras)
        choices = [("", "---------")] + [
            (node.id, node.get_absolute_url()) for node in tree.iter_flat_list()
        ]
        return choices

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
        except IndexError, err:
            if self.model.on_site.count() == 0:
                raise PageTree.DoesNotExist("There exist no PageTree items! Have you install PyLucid?")
            elif filter_parent == True:
                # If all root pages not accessible for the current user
                # -> try to get the first accessable page
                return self.get_root_page(user, filter_parent=False)
            else:
                raise

    def get_pagemeta(self, request, pagetree, show_lang_errors=True):
        """
        retuns the PageMeta instance witch associated to the given >pagetree< instance.
        
        dissolving language in client favored languages
        if not exist:
            return system default language
            
        If show_lang_errors==True:
            create a page_msg if PageMeta doesn't exist in client favored language.
        """
        from pylucid_project.apps.pylucid.models import PageMeta  # against import loops.

        # client favored Language instance:
        lang_entry = request.PYLUCID.current_language

        if pagetree.page_type == pagetree.PLUGIN_TYPE:
            # Automatic create a not existing PageMeta on PluginPages
            pagemeta = PageMeta.objects.verbose_get_or_create(
                request, pagetree, lang_entry, show_lang_errors=show_lang_errors
            )
            return pagemeta

        queryset = PageMeta.objects.filter(pagetree=pagetree)
        pagemeta, tried_languages = self.get_by_prefered_language(request, queryset)

        if pagemeta is None:
            # This page doesn't exist in any languages???
            raise

        if tried_languages and show_lang_errors:
            request.page_msg.error(
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

        return pagemeta


    def get_page_from_url(self, request, url_path):
        """
        returns a tuple the page tree instance from the given url_path
        XXX: move it out from model?
        """
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()

        path = url_path.strip("/").split("/")
        page = None
        for no, page_slug in enumerate(path):
            if slugify(page_slug) != page_slug.lower():
                raise PageTree.DoesNotExist("url part %r is not slugify" % page_slug)

            try:
                page = PageTree.on_site.get(parent=page, slug=page_slug)
            except PageTree.DoesNotExist:
                etype, evalue, etb = sys.exc_info()
                evalue = etype("Wrong url %r: %s" % (page_slug, evalue))
                raise etype, evalue, etb

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

        pagemeta = self.get_pagemeta(request, pagetree, show_lang_errors=False)
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

    design = models.ForeignKey("pylucid.Design", help_text="Page Template, CSS/JS files")

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

    _url_cache = {}
    def get_absolute_url(self):
        """ absolute url *without* language code (without domain/host part) """
        if self.pk in self._url_cache:
            #print "PageTree url cache len: %s, pk: %s" % (len(self._url_cache), self.pk)
            return self._url_cache[self.pk]

        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            url = parent_shortcut + self.slug + "/"
        else:
            url = "/" + self.slug + "/"

        self._url_cache[self.pk] = url
        return url

    def save(self, *args, **kwargs):
        """ reset PageMeta and PageTree url cache """
        from pagemeta import PageMeta # against import loops.

        self._url_cache.clear()
        PageMeta._url_cache.clear()
        return super(PageTree, self).save(*args, **kwargs)

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.site

    def __unicode__(self):
        return u"PageTree %r (id: %i, site: %s, type: %s)" % (
            self.slug, self.id, self.site.domain, self.TYPE_DICT.get(self.page_type)
        )

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PageTree"
        unique_together = (("site", "slug", "parent"),)

        # FIXME: It would be great if we can order by get_absolute_url()
#        ordering = ("site", "id", "position")
        ordering = ("-lastupdatetime",)

# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageTree)



#print Wbo.objects.all()
#
#q = Wbo.objects.values('id')
#print q.query.as_sql()


#a = PageTree.objects.all().filter()
#print a
#print dir(a.query)
#print type(a.query)
#print a.query.as_sql()
