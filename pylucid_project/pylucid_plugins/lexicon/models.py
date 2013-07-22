# coding: utf-8

"""
    PyLucid lexicon models
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages
from django.core import urlresolvers
from django.core.cache import cache
from django.db import models
from django.db.models import signals
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tagging/
from tagging.fields import TagField

# http://code.google.com/p/django-tools/
from django_tools.middlewares.ThreadLocal import get_current_request
from django_tools.tagging_addon.fields import jQueryTagModelField
from django_tools.template import render
from django_tools.utils.messages import failsafe_message
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.apps.pylucid.markup.converter import apply_markup
from pylucid_project.apps.pylucid.models import Language
from pylucid_project.base_models.base_markup_model import MarkupBaseModel
from pylucid_project.base_models.base_models import BaseModelManager
from pylucid_project.base_models.many2many import AutoSiteM2M
from pylucid_project.apps.pylucid.system.permalink import plugin_permalink
from pylucid_project.pylucid_plugins import update_journal



TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


# class Links(UpdateInfoBaseModel):
#    url = models.URLField(max_length=255)
#    title = models.CharField(_('Title'), help_text=_("Url title"), max_length=255)
#    entrie = models.ForeignKey("LexiconEntry")


class LexiconEntryManager(BaseModelManager):
    """
    inherited from BaseModelManager:
        - easy_create()
        - get_lang_item()
    """
    def get_filtered_queryset(self, request, filter_language=True):
        queryset = self.model.on_site.filter(is_public=True)
        if filter_language:
            current_lang = request.PYLUCID.current_language
            queryset = queryset.filter(language=current_lang)
        return queryset

    def get_entry(self, request, term, filter_language=True):
        """
        try to return the proper LexiconEntry instance.
        create page_msg error messages and return None it term not found.
        """
        error_msg = _("Unknown lexicon term.")

        if term in ("", None):  # e.g.: term not in url or GET parameter 'empty'
            if request.user.is_staff:
                error_msg += " (No term given.)"
            messages.error(request, error_msg)
            return

        queryset = self.get_filtered_queryset(request, filter_language=filter_language)

        try:
            entry = queryset.get(term=term)
        except self.model.DoesNotExist, err:
            if settings.DEBUG or request.user.is_staff:
                error_msg += " (term: %r, original error: %s)" % (term, err)
            messages.error(request, error_msg)
        else:
            return entry


class LexiconEntry(AutoSiteM2M, MarkupBaseModel, UpdateInfoBaseModel):
    """
    A lexicon entry.

    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display

    inherited attributes from MarkupBaseModel:
        content field
        markup field
        get_html() method

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    objects = LexiconEntryManager()

    term = models.CharField(_('Term'), help_text=_("Term in primitive form"), max_length=255)
    language = models.ForeignKey(Language)
    alias = TagField(# from django-tagging
        help_text=mark_safe(
            _('alias for this entry. <a href="%s" class="openinwindow"'
            ' title="Information about tag splitting.">tag format help</a>') % TAG_INPUT_HELP_URL
        )
    )
    tags = jQueryTagModelField()  # a django-tagging model field modified by django-tools
    short_definition = models.CharField(_('Short definition'),
        help_text=_("A short explain."), max_length=255
    )

    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def __init__(self, *args, **kwargs):
        super(LexiconEntry, self).__init__(*args, **kwargs)

        # Change field meta data in a DRY way
        content_field = self._meta.get_field_by_name("content")[0]
        content_field.help_text = _("Explain the term")

    def save(self, *args, **kwargs):
        """
        Save and update the cache
        """
        super(LexiconEntry, self).save(*args, **kwargs)

        try:
            cache.smooth_update()  # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

    def get_name(self):
        """ e.g. for pylucid comment """
        return self.term

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
        if not self.is_public:  # Don't list non public articles
            return

        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "language": self.language,
            "object_url": self.get_absolute_url(),
            "title": _("New lexicon entry '%s'.") % self.term,
        }

    def get_absolute_url(self):
        viewname = "Lexicon-detail_view"
        reverse_kwargs = {"term":self.term}  # slugify(self.term)
        try:
            # This only worked inner lucidTag
            return urlresolvers.reverse(viewname, kwargs=reverse_kwargs)
        except urlresolvers.NoReverseMatch:
            # Use the first PluginPage instance
            from pylucid_project.apps.pylucid.models import PluginPage  # import here, against import loops
            try:
                return PluginPage.objects.reverse("lexicon", viewname, kwargs=reverse_kwargs)
            except urlresolvers.NoReverseMatch:
                return "/?lexicon=%s" % self.term

    def get_permalink(self, request):
        """ permalink to this entry detail view """
        absolute_url = self.get_absolute_url()  # Absolute url to this entry
        permalink = plugin_permalink(request, absolute_url)
        return permalink

    def __unicode__(self):
        return self.term

    class Meta:
        unique_together = (("language", "term"),)
        ordering = ('term',)


signals.post_save.connect(receiver=update_journal.save_receiver, sender=LexiconEntry)

# Bug in django tagging?
# http://code.google.com/p/django-tagging/issues/detail?id=151#c2
# try:
#    tagging.register(BlogEntry)
# except tagging.AlreadyRegistered: # FIXME
#    pass
