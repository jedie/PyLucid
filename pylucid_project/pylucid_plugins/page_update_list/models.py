# coding:utf-8

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager

from pylucid.system.auto_model_info import UpdateInfoBaseModel
from pylucid.models import Language


class UpdateData(models.Model):
    """ List of all last update data, used for creating the last update table. """
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        null=True, blank=True, # <- If the model used outsite a real request (e.g. unittest, db shell)
        help_text="User as last edit the current page.",)

    site = models.ForeignKey(Site, default=Site.objects.get_current)
    on_site = CurrentSiteManager()

    # Content-object field
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s"
    )
    object_url = models.URLField(verbose_name=_('object url'), help_text="absolute url to the item.",)

    lang = models.ForeignKey(Language)

    title = models.CharField(blank=True, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )


#class UpdateDataManager(models.Manager):
#    def add_to_update_list(self, request, update_list, max_count):
#        """ Add last updates to pylucid_plugins.page_update_list """
#        queryset = self.model.objects.order_by('-lastupdatetime')[:max_count]
#        for item in queryset:
#            update_list.add(
#                lastupdatetime=item.lastupdatetime,
#                lastupdateby=item.lastupdateby,
#                content_type="blog entry",
#                language=item.lang,
#                url=item.get_absolute_url(),
#                title=item.headline
#            )


class LastUpdateObjects(UpdateInfoBaseModel):
    """ Witch objects should be listet in the last update table? """
#    objects = UpdateDataManager()

    site = models.ForeignKey(Site, default=Site.objects.get_current)
    on_site = CurrentSiteManager()

    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s"
    )
    staff_only = models.BooleanField(
        default=True, help_text="Viewable only by staff users?"
    )
