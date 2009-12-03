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

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tagging/
from tagging.fields import TagField

# http://code.google.com/p/django-tools/
from django_tools import model_utils

from pylucid.models.base_models import UpdateInfoBaseModel, BaseModel, BaseModelManager



TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"



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

    pagetree = models.ForeignKey("pylucid.PageTree")
    language = models.ForeignKey("pylucid.Language")

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

    _url_cache = {}
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

    def get_permalink(self):
        """
        return a permalink. Use page slug/name/title or nothing as additional text.
        """
        from pylucid.preference_forms import SystemPreferencesForm # FIXME: against import loops.

        sys_pref_form = SystemPreferencesForm()
        sys_pref = sys_pref_form.get_preferences()
        use_additions = sys_pref.get("permalink_additions", SystemPreferencesForm.PERMALINK_USE_TITLE)

        do_slugify = False
        if use_additions == SystemPreferencesForm.PERMALINK_USE_TITLE:
            # Append the PageMeta title (language dependent)
            addition_txt = self.get_title()
            do_slugify = True
        elif use_additions == SystemPreferencesForm.PERMALINK_USE_NAME:
            addition_txt = self.get_name()
            do_slugify = True
        elif use_additions == SystemPreferencesForm.PERMALINK_USE_SLUG:
            addition_txt = self.pagetree.slug
        else:
            addition_txt = ""

        if do_slugify:
            addition_txt = slugify(addition_txt)

        url = reverse('PyLucid-permalink', kwargs={'page_id': self.pagetree.id, 'url_rest': addition_txt})
        return url

    def save(self, *args, **kwargs):
        """ reset PageMeta and PageTree url cache """
        self._url_cache.clear()
        self.pagetree._url_cache.clear()
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
