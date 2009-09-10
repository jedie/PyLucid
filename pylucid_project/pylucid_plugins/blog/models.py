# coding: utf-8

"""
    PyLucid blog models
    ~~~~~~~~~~~~~~~~~~~

    Database models for the blog.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

from django.db import models
from django.core import urlresolvers
from django.db.models import signals
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tagging/
from tagging.fields import TagField

from pylucid_project.pylucid_plugins import update_journal

from pylucid.shortcuts import failsafe_message
from pylucid.models import PageContent, Language, PluginPage
from pylucid.markup.converter import apply_markup
from pylucid.models.base_models import AutoSiteM2M, UpdateInfoBaseModel


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class BlogEntry(AutoSiteM2M, UpdateInfoBaseModel):
    """
    A blog entry
    
    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    headline = models.CharField(_('Headline'),
        help_text=_("The blog entry headline"), max_length=255
    )
    content = models.TextField(_('Content'))
    language = models.ForeignKey(Language)
    markup = models.IntegerField(
        max_length=1, choices=PageContent.MARKUP_CHOICES,
        help_text="the used markup language for this entry",
    )
    tags = TagField(# from django-tagging
        help_text=mark_safe(
            _('tags for this entry. <a href="%s" class="openinwindow"'
            ' title="Information about tag splitting.">tag format help</a>') % TAG_INPUT_HELP_URL
        )
    )
    is_public = models.BooleanField(
        default=True, help_text="Is post public viewable?"
    )

    def get_update_info(self):
        """ update info for update_journal.models.UpdateJournal used by update_journal.save_receiver """
        if not self.is_public: # Don't list non public articles
            return

        return {
            "lastupdatetime": self.lastupdatetime,
            "user_name": self.lastupdateby,
            "language": self.language,
            "object_url": self.get_absolute_url(),
            "title": self.headline,
        }

    def get_absolute_url(self):
        url_title = slugify(self.headline)
        viewname = "Blog-detail_view"
        reverse_kwargs = {"id": self.pk, "title":url_title}
        try:
            # This only worked inner lucidTag
            return urlresolvers.reverse(viewname, kwargs=reverse_kwargs)
        except urlresolvers.NoReverseMatch:
            # Use the first PluginPage instance
            try:
                return PluginPage.objects.reverse("blog", viewname, kwargs=reverse_kwargs)
            except:
                failsafe_message("No blog PagePlugin found! Please create one.")
                return "#No-Blog-PagePlugin-exists"

    def get_html(self):
        """
        returns the generate html code from the content applyed the markup.
        """
        return apply_markup(self.content, self.markup, failsafe_message)

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')


signals.post_save.connect(receiver=update_journal.save_receiver, sender=BlogEntry)

# Bug in django tagging?
# http://code.google.com/p/django-tagging/issues/detail?id=151#c2
#try:
#    tagging.register(BlogEntry)
#except tagging.AlreadyRegistered: # FIXME
#    pass
