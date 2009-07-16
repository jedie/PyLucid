# coding:utf-8

from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission

from pylucid.models import TreeBaseModel
from pylucid.system.auto_model_info import UpdateInfoBaseModel

class PyLucidAdminManager(models.Manager):
    def get_for_user(self, user):
        """
        returns only the menu items, for which the user has the rights.
        TODO: Filter menu sections, too. (If there is no sub items, remove the section)
        """
        all_items = self.all()
        filtered_items = []
        for item in all_items:
            superuser_only, access_permissions = item.get_permissions()
            if superuser_only == True and user.is_superuser == False:
                continue
            if not user.has_perms(access_permissions):
                continue

            filtered_items.append(item)

        return filtered_items

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
    objects = PyLucidAdminManager()

    #TODO: check if url_name is unique. We can't set unique==True,
    #      because menu section has always url_name=None
    url_name = models.CharField(blank=True, null=True, max_length=256,
        help_text="Name of url, defined in plugin/admin_urls.py"
    )

    name = models.CharField(max_length=150, unique=True,
        help_text="Sort page name (for link text in e.g. menu)"
    )
    title = models.CharField(blank=True, null=False, max_length=256,
        help_text="A long page title (for e.g. page title or link title text)"
    )

    def get_permissions(self):
        """
        returns the access permissions for this menu entry.
        TODO: Should be cache this?
        """
        if not self.url_name: # a menu section
            return (False, ())

        # Get the view function for this url_name
        # FIXME: Can we get it faster and not with resolve the url?
        url = urlresolvers.reverse(self.url_name)
        view_func, func_args, func_kwargs = urlresolvers.resolve(url)

        # get the rights from pylucid.decorators.check_permissions
        access_permissions = view_func.permissions
        superuser_only = view_func.superuser_only

        return (superuser_only, access_permissions)

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
