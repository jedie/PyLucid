# coding: utf-8

"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
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
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal
from django_tools.models import UpdateInfoBaseModel

from pylucid_migration.base_models.base_models import BaseModel
from pylucid_migration.base_models.permissions import PermissionsBase
from pylucid_migration.models.pagetree import PageTree
from pylucid_migration.models.language import Language


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
    pagetree = models.ForeignKey(PageTree)
    language = models.ForeignKey(Language)

    name = models.CharField(blank=True, max_length=150,
        help_text="Sort page name (for link text in e.g. menu)"
    )
    title = models.CharField(blank=True, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )

    tags = models.CharField(max_length=765) # a django-tagging model field modified by django-tools

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

    def get_absolute_url(self):
        """ absolute url *with* language code (without domain/host part) """
        lang_code = self.language.code
        page_url = self.pagetree.get_absolute_url()
        url = "/" + lang_code + page_url
        return url

    def get_permalink(self):
        """
        return a permalink. Use page slug/name/title or nothing as additional text.
        """
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
        return url

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
        app_label = u'pylucid_migration'
        db_table = u'pylucid_pagemeta'
        verbose_name_plural = verbose_name = "PageMeta"
        unique_together = (("pagetree", "language"),)
        ordering = ("-lastupdatetime",)
#        ordering = ("pagetree", "language")

