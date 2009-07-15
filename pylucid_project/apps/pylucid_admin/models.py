# coding:utf-8

from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission

from pylucid.models import TreeBaseModel
from pylucid.system.auto_model_info import UpdateInfoBaseModel


class PyLucidAdminPage(TreeBaseModel, UpdateInfoBaseModel):
    """
    PyLucid Admin page tree
    
    inherited attributes from TreeBaseModel:
        parent
        position

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    name = models.CharField(max_length=150, unique=True,
        help_text="Sort page name (for link text in e.g. menu)"
    )
    title = models.CharField(blank=True, null=False, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )

    #TODO: check if url_name is unique. We can't set unique==True,
    #      because menu section has always url_name=None
    url_name = models.CharField(blank=True, null=True, max_length=256,
        help_text="Name of url, defined in plugin/admin_urls.py"
    )
    access_permissions = models.ManyToManyField(Permission, verbose_name=_('access permissions'), blank=True,
        help_text="The user must have these permissions to see the menu point."
    )
    superuser_only = models.BooleanField(
        help_text="Limit the access to superusers only. If True the access permission list would be ignored!"
    )

    def add_access_permissions(self, permissions):
        """
        Add all access permissions from the given list.
        FIXME: Get the ContentType instance seems to be ugly?
        """
        assert isinstance(permissions, (list, tuple))

        for permission in permissions:
            app_label, codename = permission.split(".")
            action, modelname = codename.split("_")

            content_type = ContentType.objects.get(app_label=app_label, model=modelname)
            perm = Permission.objects.get(content_type=content_type, codename=codename)
            self.access_permissions.add(perm)

    def __unicode__(self):
        return u"PyLucidAdminPage %r (%r)" % (self.name, self.get_absolute_url())

    def get_absolute_url(self):
        """
        absolute url (without domain/host part)
        TODO: Should be used a cache here?
        """
        if self.url_name:
            return urlresolvers.reverse(viewname=self.url_name)
        else:
            return ""

    class Meta:
        ordering = ("url_name",)
