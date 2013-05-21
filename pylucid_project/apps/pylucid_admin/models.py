# coding:utf-8

"""
    PyLucid admin menu models
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from django_tools.middlewares import ThreadLocal
from django_tools.models import UpdateInfoBaseModel
from django_tools.utils.messages import failsafe_message

from pylucid_project.apps.pylucid.tree_model import BaseTreeModel, TreeManager, TreeGenerator


class PyLucidAdminManager(TreeManager):
    def get_tree_for_user(self, user):
        filtered_items = self.get_for_user(user)
        tree = TreeGenerator(filtered_items)
        #tree.debug()

        # Hide categories, if they has no sub entry links
        # (e.g. user has no right to use any sub entry views)        
        for node in tree.iter_flat_list():
            if not node.data["absolute_url"] and not node.subnodes:
                node.visible = False

        return tree

    def get_for_user(self, user):
        """
        returns only the menu items, for which the user has the rights.
        """
        all_items = self.all().order_by("position", "name")
        filtered_items = []
        for item in all_items:
            access_permissions = item.get_permissions()
            superuser_only, permissions, must_staff = access_permissions

            if superuser_only == True and user.is_superuser != True:
                continue
            if must_staff == True and user.is_staff != True:
                continue
            if not user.has_perms(permissions):
                continue

            filtered_items.append({
                "id": item.id,
                "parent": getattr(item.parent, "id", None),
                "absolute_url": item.get_absolute_url(),
                "name": item.name,
                "title": item.title,
            })

        return filtered_items

class PyLucidAdminPage(BaseTreeModel, UpdateInfoBaseModel):
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

    get_pagetree = models.BooleanField(default=False,
        verbose_name="get PageTree",
        help_text="Add current PageTree ID via GET Parameter to the url, if available"
    )
    get_pagemeta = models.BooleanField(default=False,
        verbose_name="get PageMeta",
        help_text="Add current PageMeta ID via GET Parameter to the url, if available"
    )
    get_page = models.BooleanField(default=False,
        verbose_name="get PageContent/PluginPage",
        help_text="Add current PageContent or current PluginPage ID via GET Parameter to the url, if available"
    )

    def clean_fields(self, exclude):
        # check if parent is the same entry: child <-> parent loop:
        super(PyLucidAdminPage, self).clean_fields(exclude)

        # check if url_name is unique. We can't set unique==True,
        # because menu section has always url_name=None
        if "url_name" not in exclude and self.url_name is not None:
            queryset = PyLucidAdminPage.objects.filter(url_name=self.url_name)

            # Exclude the current object from the query if we are editing an
            # instance (as opposed to creating a new one)
            if self.pk is not None:
                queryset = queryset.exclude(pk=self.pk)

            exists = queryset.count()
            if exists:
                msg = "url name %r exist!" % self.url_name
                message_dict = {"url_name": (msg,)}
                raise ValidationError(message_dict)

    def get_url(self):
        """
        reverse the url name.
        
        Create error message if NoReverseMatch and return None.
        e.g.: Plugin deleted in filesystem, but still exist in database.
        
        FIXME: Can we get it faster and not with resolve the url?
        """
        try:
            url = urlresolvers.reverse(self.url_name)
        except urlresolvers.NoReverseMatch, err:
            msg = (
                "Can't resolve url %r for plugin %r: %s"
                " - (To fix this: run 'install plugins' again.)"
            ) % (self.url_name, self.name, err)
            failsafe_message(msg)
        else:
            return url

    def get_permissions(self):
        """
        returns the access permissions for this menu entry.
        TODO: Should be cache this?
        """
        if not self.url_name: # a menu section
            # TODO: Check if at least one sub entry is accessible.
            return (False, (), False)

        url = self.get_url()
        if url is None: # can't resolve url, message was created.
            return (True, (), True) # view can only superusers use

        # Get the view function for this url_name
        view_func, func_args, func_kwargs = urlresolvers.resolve(url)

        # get the rights from pylucid_project.apps.pylucid.decorators.check_permissions
        try:
            access_permissions = view_func.access_permissions
        except AttributeError, err:
            # If no permissions available, fallback to superuser only
            request = ThreadLocal.get_current_request()
            if settings.DEBUG or request.user.is_staff:
                messages.error(request, (
                    "The view %s for url %r has no permissions attribute!"
                    " Please use pylucid_project.apps.pylucid.decorators.check_permissions!"
                    ) % (view_func.__name__, self.url_name)
                )
            access_permissions = (True, (), True)

        return access_permissions

#    def save(self, *args, **kwargs):
#        """
#        After change, deletes panel_extra from cache.
#        cache filled in pylucid_plugins.admin_menu.views.panel_extras()
#        """
#        for user_id in User.objects.values_list('id', flat=True):
#            cache_key = "panel_extras_%s" % user_id
#            cache.delete(cache_key)
#
#        return super(PyLucidAdminPage, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"PyLucidAdminPage %r (%r)" % (self.name, self.get_absolute_url())

    def get_absolute_url(self):
        """
        absolute url (without domain/host part)
        TODO: Should be used a cache here?
        """
        if not self.url_name:
            return "" # menu section

        url = self.get_url()
        if url is None: # can't resolve url, message was created.
            return "#resolve-error" # XXX: return something else?

        request = ThreadLocal.get_current_request()
        get_data = {}
        if self.get_pagetree and hasattr(request.PYLUCID, "pagetree"):
            get_data["pagetree"] = request.PYLUCID.pagetree.pk
        if self.get_pagemeta and hasattr(request.PYLUCID, "pagemeta"):
            get_data["pagemeta"] = request.PYLUCID.pagemeta.pk
        if self.get_page:
            if hasattr(request.PYLUCID, "pagecontent"):
                get_data["pagecontent"] = request.PYLUCID.pagecontent.pk
            elif hasattr(request.PYLUCID, "pluginpage"):
                get_data["pluginpage"] = request.PYLUCID.pluginpage.pk

        if get_data:
            # FIXME: There must be a better was to to this.
            # TODO: escape it.
            url += "?" + "&".join(["%s=%s" % (key, value) for key, value in get_data.items()])

        return url

    class Meta:
        verbose_name = _('PyLucid admin page')
        verbose_name_plural = _('PyLucid admin pages')
        ordering = ("name", "url_name",)
